# Generated by Django 5.1.3 on 2025-05-11 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_doctor_department_doctor_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
