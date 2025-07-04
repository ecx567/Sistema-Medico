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
    CONSULTATION_TYPES = (
        ('normal', 'Consulta General'),
        ('specialty', 'Consulta por Especialidad'),
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
    consultation_type = models.CharField(
        max_length=20, 
        choices=CONSULTATION_TYPES,
        default="normal",
        verbose_name="Tipo de consulta"
    )
    medical_history_file = models.FileField(
        upload_to='medical_histories/',
        blank=True,
        null=True,
        verbose_name="Archivo de historial médico"
    )

    payment_status = models.BooleanField(
        default=False,
        verbose_name="Estado de pago"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monto pagado"
    )
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    # def __str__(self):
    #     return f"Cita: {self.patient.username} con {self.doctor.username} el {self.appointment_date}"
    
    def __str__(self):
        return f"Cita: {self.doctor.get_full_name()} con {self.patient.get_full_name()} - {self.appointment_date}"
    
    def has_reminder(self):
        """Verifica si la cita tiene recordatorios enviados"""
        return hasattr(self, 'reminders') and self.reminders.exists()

    @property
    def status_badge(self):
        """Devuelve la clase CSS para el badge según el estado"""
        status_classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-success',
            'cancelled': 'badge-danger',
            'completed': 'badge-info',
            'no_show': 'badge-secondary'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    @property
    def price(self):
        """Devuelve el precio de la consulta según el tipo"""
        if hasattr(self, 'consultation_type') and self.consultation_type == 'specialty':
            return "100.00"
        return "50.00"
    
    class Meta:
        ordering = ["-appointment_date", "-appointment_time"]
        # Ensure no double bookings for same doctor at same time
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        unique_together = ["doctor", "appointment_date", "appointment_time"]

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.get_full_name()} on {self.appointment_date} at {self.appointment_time}"

#

class Prescription(models.Model):
    booking = models.OneToOneField(
        "Booking", on_delete=models.CASCADE, related_name="prescription"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        #"accounts.User",
        on_delete=models.CASCADE,
        related_name="prescriptions_given",
        limit_choices_to={"role": "doctor"},
    )
    patient = models.ForeignKey(
        #"accounts.User",
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions_received",
        limit_choices_to={"role": "patient"},
    )
    symptoms = models.TextField()
    diagnosis = models.TextField()
    medications = RichTextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.patient.get_full_name()} by Dr. {self.doctor.get_full_name()}"

    class Meta:
        ordering = ["-created_at"]
