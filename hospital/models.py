from django.db import models
from django.utils import timezone

class Hospital(models.Model):
    name = models.CharField(max_length=100)
    total_beds = models.IntegerField(default=0)
    available_beds = models.IntegerField(default=0)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    CONDITION_CHOICES = [
        ('Stable', 'Stable'),
        ('Critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    date_of_birth = models.DateField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    situation = models.TextField()
    symptoms = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    family_phone = models.CharField(max_length=15)
    appointment_date = models.DateField()
    registration_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    bed_number = models.IntegerField(null=True, blank=True)
    token = models.CharField(max_length=8, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    queue_position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.token}"

    def save(self, *args, **kwargs):
        if not self.token:
            # Generate a unique token
            import random
            import string
            while True:
                token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Patient.objects.filter(token=token).exists():
                    self.token = token
                    break
        
        if self.status == 'Waiting' and not self.queue_position:
            # Assign queue position based on registration time
            self.queue_position = Patient.objects.filter(
                hospital=self.hospital,
                status='Waiting',
                registration_time__lt=self.registration_time
            ).count() + 1
        
        super().save(*args, **kwargs)

class Doctor(models.Model):
    DEPARTMENT_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Cardiology')
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    is_available = models.BooleanField(default=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    def __str__(self):
        return f"Dr. {self.name} - {self.department}"

    def save(self, *args, **kwargs):
        # Update is_available based on status
        self.is_available = (self.status == 'Available')
        super().save(*args, **kwargs)