from django.db import models
from django.conf import settings
from ckeditor5.fields import RichTextField


class Booking(models.Model):
    """Modelo para gestionar citas médicas"""
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
        ('no_show', 'No Show'),
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={"role": "doctor"},
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        limit_choices_to={"role": "patient"},
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cita: {self.patient.username} con {self.doctor.username} el {self.appointment_date}"
    
    def has_reminder(self):
        """Verifica si la cita tiene recordatorios enviados"""
        return hasattr(self, 'reminders') and self.reminders.exists()

    class Meta:
        ordering = ["-appointment_date", "-appointment_time"]
        # Ensure no double bookings for same doctor at same time
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        unique_together = ["doctor", "appointment_date", "appointment_time"]

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.get_full_name()} on {self.appointment_date} at {self.appointment_time}"


class Prescription(models.Model):
    booking = models.OneToOneField(
        "Booking", on_delete=models.CASCADE, related_name="prescription"
    )
    doctor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="prescriptions_given",
    )
    patient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="prescriptions_received",
    )
    symptoms = models.TextField()
    diagnosis = models.TextField()
    medications = RichTextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.patient} by Dr. {self.doctor}"

    class Meta:
        ordering = ["-created_at"]
