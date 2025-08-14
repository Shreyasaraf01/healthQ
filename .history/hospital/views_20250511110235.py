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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def health_bot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()

        # Simple rule-based responses
        responses = {
            'fever': "For fever, rest and stay hydrated. If temperature is above 102°F or persists, consult a doctor.",
            'headache': "For headaches, rest in a dark room and stay hydrated. If severe or persistent, seek medical help.",
            'cough': "For cough, drink warm fluids and rest. If severe or with other symptoms, see a doctor.",
            'cold': "For cold, rest, stay hydrated, and use over-the-counter remedies. If symptoms worsen, see a doctor.",
            'pain': "For pain, rest the affected area. If severe or persistent, consult a healthcare provider.",
            'diet': "A balanced diet includes fruits, vegetables, whole grains, and lean proteins. Consult a nutritionist for personalized advice.",
            'exercise': "Regular exercise is important. Start with 30 minutes of moderate activity daily. Consult a doctor before starting a new routine.",
            'sleep': "Aim for 7-9 hours of sleep. Maintain a regular schedule and avoid screens before bed.",
            'stress': "Practice deep breathing, meditation, or yoga. If stress affects daily life, consider professional help.",
            'emergency': "For emergencies, call emergency services immediately or visit the nearest hospital.",
            'fever': "For fever, rest and stay hydrated. If temperature is above 102°F or persists, consult a doctor.",
            'headache': "For headaches, rest in a dark room and stay hydrated. If severe or persistent, seek medical help.",
            'cough': "For cough, drink warm fluids and rest. If severe or with other symptoms, see a doctor.",
            'cold': "For cold, rest, stay hydrated, and use over-the-counter remedies. If symptoms worsen, see a doctor.",
            'pain': "For pain, rest the affected area. If severe or persistent, consult a healthcare provider.",
            'diet': "A balanced diet includes fruits, vegetables, whole grains, and lean proteins. Consult a nutritionist for personalized advice.",
            'exercise': "Regular exercise is important. Start with 30 minutes of moderate activity daily. Consult a doctor before starting a new routine.",
            'sleep': "Aim for 7-9 hours of sleep. Maintain a regular schedule and avoid screens before bed.",
            'stress': "Practice deep breathing, meditation, or yoga. If stress affects daily life, consider professional help.",
            'emergency': "For emergencies, call emergency services immediately or visit the nearest hospital.",
            'anxiety': "Try breathing exercises, talk to someone you trust, and consult a mental health professional if it persists.",
            'depression': "Seek support from a mental health professional. You're not alone, and help is available.",
            'diabetes': "Monitor your blood sugar, eat a balanced diet, and follow your medication plan. Regular checkups are crucial.",
            'hypertension': "Limit salt intake, maintain a healthy weight, and follow your doctor's medication and lifestyle advice.",
            'hydration': "Drink at least 8 glasses of water daily. Increase intake during hot weather or physical activity.",
            'first aid': "For minor cuts, clean with water, apply antiseptic, and cover with a clean bandage. Seek help for serious injuries.",
            'hygiene': "Wash hands frequently, brush teeth twice daily, and bathe regularly to maintain good hygiene.",
            'vaccination': "Stay up to date with routine immunizations. Consult your doctor for a recommended schedule.",
            'covid': "Wear masks in crowded places, maintain distance, and stay updated on vaccination boosters.",
            'burn': "For minor burns, cool with running water, avoid ice, and apply a sterile dressing. Seek help for severe burns.",
            'fracture': "Immobilize the area and seek immediate medical attention. Do not try to reset the bone yourself.",
            'allergy': "Avoid allergens and use antihistamines. In case of severe reactions, use an epinephrine auto-injector and call emergency services.",
            'pregnancy': "Follow regular prenatal checkups, eat healthy, and avoid smoking or alcohol. Consult your OB/GYN for detailed guidance.",
            'child care': "Ensure vaccinations, proper nutrition, and a safe environment. Monitor growth and developmental milestones.",
            'menstruation': "Track cycles, use hygienic products, and consult a gynecologist if you experience irregularities or discomfort.",
            'obesity': "Adopt a healthy lifestyle with a balanced diet and regular exercise. Seek guidance from a dietitian or doctor.",
            'back pain': "Maintain good posture, use ergonomic chairs, and stretch regularly. Seek a doctor's advice if persistent.",
            'skin care': "Use sunscreen, stay hydrated, and follow a gentle skincare routine. Consult a dermatologist for issues.",
            'hair loss': "Maintain scalp hygiene, avoid harsh products, and consider consulting a dermatologist for treatments.",
        }

        # Find matching response
        bot_reply = "I'm a simple health assistant. For medical advice, please consult a healthcare professional."
        for key, response in responses.items():
            if key in user_message:
                bot_reply = response
                break

        return JsonResponse({'reply': bot_reply})
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