from django.urls import path
from .views import (
    home,
    get_hospitals,
    get_patients,
    get_doctors,                
    dashboard,
    doctor_assignment,
    doctor_list,
    patient_register,
    queue_management,
    bed_status,
    contact_us,
    health_bot_api,
)

urlpatterns = [
    path('', home, name='home'),
    path('dashboard', dashboard, name='dashboard'),
    path('hospitals/', get_hospitals, name='get_hospitals'),
    path('patients/', get_patients, name='get_patients'),
    path('doctors/', get_doctors, name='get_doctors'),  # API endpoint
    path('doctor-assignment/', doctor_assignment, name='doctor_assignment'),  # HTML view
    path('doctors/', doctor_list, name='doctor-list'),
    path('doctors-api/', doctor_list, name='doctor-list-api'),
    path('register-patient/', patient_register, name='patient_register'),
    path('queue-management/', queue_management, name='queue_management'),  # HTML view
    path('bed-status/', bed_status, name='bed_status'),  # HTML view
    path('contact-us/', contact_us, name='contact_us'),  # HTML view
    path('api/health-bot/',health_bot_api, name = 'health_bot_api'),
]

