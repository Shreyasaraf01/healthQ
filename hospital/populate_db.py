import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthQ.settings")
django.setup()

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthQ.settings')  # Replace 'healthQ' with your project name
django.setup()

from hospital.models import Hospital, Patient

hospital = Hospital.objects.create(name="City Hospital", location="Downtown")
Patient.objects.create(hospital=hospital, name="John Doe", condition="Stable", situation="Normal", symptoms="Cough", queue_position=1)