from faker import Faker
import random
from hospital.models import Hospital, Patient

fake = Faker()

def create_mock_hospitals(n=5):
    for _ in range(n):
        Hospital.objects.create(
            name=fake.company() + " Hospital",
            location=fake.city(),
            total_beds=random.randint(50, 500),
            available_beds=random.randint(0, 50),
        )

def create_mock_patients(n=10):
    for _ in range(n):
        Patient.objects.create(
            name=fake.name(),
            age=random.randint(18, 80),
            condition=random.choice(["Critical", "Stable"]),
            hospital=Hospital.objects.order_by('?').first(),
        )
