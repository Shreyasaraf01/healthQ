from django.contrib import admin

from django.contrib import admin
from .models import Hospital, Patient, Doctor  # Import your models

# Register models
admin.site.register(Hospital)
admin.site.register(Patient)
admin.site.register(Doctor)
