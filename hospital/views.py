from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Hospital, Patient, Doctor
from .serializers import HospitalSerializer, PatientSerializer, DoctorSerializer
import json

# API views
@api_view(['GET'])
def get_hospitals(request):
    hospitals = Hospital.objects.all()
    serializer = HospitalSerializer(hospitals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_patients(request):
    patients = Patient.objects.all().order_by('queue_position')
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
    recent_patients = Patient.objects.order_by('-id')[:5]  # Optional: last 5 entries

    hospital_names = []
    patient_counts = []

    for hospital in hospitals:
        hospital_names.append(hospital.name)
        patient_counts.append(Patient.objects.filter(hospital=hospital).count())

    return render(request, 'hospital/dashboard.html', {
        'hospital_count': hospitals.count(),
        'patient_count': patients,
        'recent_patients': recent_patients,  # Optional
        'hospital_names': json.dumps(hospital_names),
        'patient_counts': json.dumps(patient_counts),
    })


# Patient Registration View
def patient_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        hospital_id = request.POST.get('hospital')

        # Fetch hospital
        try:
            hospital = Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            return render(request, 'hospital/patient_register.html', {
                'error': 'Selected hospital does not exist.',
                'hospitals': Hospital.objects.all()
            })

        # Generate queue position as token number
        queue_position = Patient.objects.filter(hospital=hospital).count() + 1

        # Create patient
        patient = Patient.objects.create(
            name=name,
            age=age,
            hospital=hospital,
            queue_position=queue_position
        )

        # Render token_generated.html with patient data
        return render(request, 'hospital/token_generated.html', {
            'patient': patient,
            'token_number': queue_position,
            'hospital': hospital
        })

    # If GET request, render form
    hospitals = Hospital.objects.all()
    return render(request, 'hospital/patient_register.html', {
        'hospitals': hospitals
    })


# Queue Management View
def queue_management(request):
    waiting = Patient.objects.filter(status='waiting')
    in_progress = Patient.objects.filter(status='in_progress')
    completed = Patient.objects.filter(status='completed')

    return render(request, 'hospital/queue_management.html', {
        'waiting': waiting,
        'in_progress': in_progress,
        'completed': completed
    })

# Bed Status View
def bed_status(request):
    hospitals = Hospital.objects.all()
    return render(request, 'hospital/bed_status.html', {'hospitals': hospitals})

# Doctor Assignment View
def doctor_assignment(request):
    doctors = Doctor.objects.all()  
    return render(request, 'hospital/doctor_assignment.html', {'doctors': doctors})

def contact_us(request):
    return render(request, 'hospital/contact_us.html')
