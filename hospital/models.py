from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    total_beds = models.IntegerField()
    available_beds = models.IntegerField()

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    condition = models.CharField(choices=[("Critical", "Critical"), ("Stable", "Stable")], max_length=10)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    queue_position = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Assign priority: Critical patients get position 1
        if self.condition == "Critical":
            self.queue_position = 1
        else:
            last_patient = Patient.objects.filter(hospital=self.hospital).order_by('-queue_position').first()
            self.queue_position = (last_patient.queue_position + 1) if last_patient else 1
        super().save(*args, **kwargs)


class Doctor(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('on_leave', 'On Leave'),
    ]

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    doctor_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Dr. {self.name} - {self.department} ({self.get_status_display()})"