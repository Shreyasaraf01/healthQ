from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Hospital, Patient, Doctor
from .serializers import HospitalSerializer, PatientSerializer, DoctorSerializer
from django.http import JsonResponse
from hospital.ai.ai_model import predict_queue, predict_bed
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
import random
import string
from django.conf import settings
api_key = settings.OMNIDIMENSION_API_KEY
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


import requests

@csrf_exempt
def health_bot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Send to Omnidimension API
            response = requests.post(
                "https://backend.omnidim.io/api/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.OMNIDIMENSION_API_KEY}"
                },
                json={
                    "message": user_message
                }
            )

            if response.status_code == 200:
                reply_data = response.json()
                bot_reply = reply_data.get("reply", "Sorry, I couldn't process that.")
                return JsonResponse({'reply': bot_reply})
            else:
                return JsonResponse({'error': 'Bot API error'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# API views
@api_view(['GET'])
def get_hospitals(request):
    hospitals = Hospital.objects.all()
    serializer = HospitalSerializer(hospitals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_patients(request):
    patients = Patient.objects.filter(status='Waiting').order_by('registration_time')
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_doctors(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'hospital/doctor_list.html', {'doctors': doctors})

# Home Page View
def home(request):
    return render(request, 'hospital/home.html')

# Dashboard View
def dashboard(request):
    hospitals = Hospital.objects.all()
    patients = Patient.objects.count()
    recent_patients = Patient.objects.order_by('-id')[:5]  # Last 5 entries

    hospital_names = []
    patient_counts = []

    for hospital in hospitals:
        hospital_names.append(hospital.name)
        patient_counts.append(Patient.objects.filter(hospital=hospital).count())

    return render(request, 'hospital/dashboard.html', {
        'hospital_count': hospitals.count(),
        'patient_count': patients,
        'recent_patients': recent_patients,
        'hospital_names': json.dumps(hospital_names),
        'patient_counts': json.dumps(patient_counts),
    })

def generate_token():
    """Generate a unique token for patient registration"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@transaction.atomic
def patient_register(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            age = request.POST.get('age')
            dob = request.POST.get('dob')
            condition = request.POST.get('condition')
            situation = request.POST.get('situation')
            symptoms = request.POST.get('symptoms')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            family_phone = request.POST.get('familyPhone')
            appointment_date = request.POST.get('appointmentDate')
            hospital_id = request.POST.get('hospital')

            # Validate phone numbers
            if phone == family_phone:
                return render(request, 'hospital/patient_register.html', {
                    'error': 'Patient phone number and family phone number cannot be the same',
                    'hospitals': Hospital.objects.all()
                })

            # Get hospital
            try:
                hospital = Hospital.objects.get(id=hospital_id)
            except Hospital.DoesNotExist:
                return render(request, 'hospital/patient_register.html', {
                    'error': 'Selected hospital does not exist',
                    'hospitals': Hospital.objects.all()
                })

            # Generate token
            token = generate_token()

            # Create patient record
            patient = Patient.objects.create(
                name=name,
                age=age,
                date_of_birth=dob,
                condition=condition,
                situation=situation,
                symptoms=symptoms,
                email=email,
                phone=phone,
                family_phone=family_phone,
                appointment_date=appointment_date,
                hospital=hospital,
                registration_time=timezone.now(),
                token=token
            )

            # Handle critical patients
            if condition == 'Critical':
                # Check if hospital has available beds
                if hospital.available_beds > 0:
                    # Admit patient directly
                    patient.status = 'Admitted'
                    patient.bed_number = hospital.total_beds - hospital.available_beds + 1
                    patient.save()
                    
                    # Update hospital bed count
                    hospital.available_beds -= 1
                    hospital.save()
                    
                    return render(request, 'hospital/admitted.html', {
                        'patient': patient,
                        'hospital': hospital
                    })
                else:
                    # If no beds available, add to queue
                    patient.status = 'Waiting'
                    patient.save()
                    messages.warning(request, 'No beds available. Patient added to waiting list.')
            else:
                # For stable patients, add to queue
                patient.status = 'Waiting'
                patient.save()

            # Return success with token
            return render(request, 'hospital/patient_register.html', {
                'token': token,
                'hospitals': Hospital.objects.all()
            })

        except Exception as e:
            return render(request, 'hospital/patient_register.html', {
                'error': f'An error occurred: {str(e)}',
                'hospitals': Hospital.objects.all()
            })

    # GET request - show registration form
    return render(request, 'hospital/patient_register.html', {
        'hospitals': Hospital.objects.all()
    })

# Queue Management View with AI Predictions
def queue_management(request):
    patients = Patient.objects.filter(status='Waiting').order_by('registration_time')

    predictions = []
    for idx, patient in enumerate(patients):
        predicted_time = predict_queue(
            patient.hospital.name,
            patient.condition,
            patient.situation,
            patient.symptoms
        )
        predictions.append({
            'name': patient.name,
            'department': patient.hospital.name,
            'queue_position': idx + 1,
            'predicted_waiting_time': predicted_time if predicted_time is not None else "N/A"
        })

    return render(request, 'hospital/queue_management.html', {
        'predictions': predictions,
    })

# Bed Status View with AI Predictions
def bed_status(request):
    hospitals = Hospital.objects.all()
    bed_predictions = []
    admitted_patients = Patient.objects.filter(status='Admitted')

    for hospital in hospitals:
        # Count patients with status 'Discharged' for this hospital
        discharged_count = Patient.objects.filter(hospital=hospital, status='Discharged').count()

        bed_predictions.append({
            'ward': hospital.name,
            'total_beds': hospital.total_beds,
            'occupied': hospital.total_beds - hospital.available_beds,
            'available': hospital.available_beds,
            'predicted_discharges': discharged_count  # Now shows actual discharges
        })

    return render(request, 'hospital/bed_status.html', {
        'bed_predictions': bed_predictions,
        'admitted_patients': admitted_patients
    })

# Doctor Assignment View
def doctor_assignment(request):
    doctors = Doctor.objects.all()  
    return render(request, 'hospital/doctor_assignment.html', {'doctors': doctors})

# Contact Us View
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # Here you can add code to save the contact form data to a database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact_us')
        
    return render(request, 'hospital/contact_us.html')