from django.contrib import admin
from .models import Hospital, Patient, Doctor

# Custom action to discharge patients
def discharge_patients(modeladmin, request, queryset):
    queryset.update(status='Discharged')
discharge_patients.short_description = "Mark selected patients as Discharged"

class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'condition', 'hospital', 'queue_position', 'status')
    list_filter = ('status', 'hospital', 'condition')
    actions = [discharge_patients]

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'status', 'hospital')
    list_filter = ('status', 'hospital')
    exclude = ('is_available',)  # Hide the is_available field in the admin form

# Register models
admin.site.register(Hospital)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Doctor, DoctorAdmin)