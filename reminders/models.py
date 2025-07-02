from django.db import models
from django.conf import settings
from bookings.models import Booking

class ReminderConfiguration(models.Model):
    """Configuración global de recordatorios"""
    hours_before = models.PositiveIntegerField(
        default=24,
        help_text="Horas antes de la cita para enviar el recordatorio"
    )
    enabled = models.BooleanField(default=True)
    email_subject = models.CharField(max_length=255, default="Recordatorio de cita médica")
    email_template_patient = models.TextField(
        default=(
            "Estimado/a {patient_name},\n\n"
            "Le recordamos que tiene una cita programada con el Dr. {doctor_name} "
            "el {appointment_date} a las {appointment_time}.\n\n"
            "Por favor, llegue con 10 minutos de anticipación.\n\n"
            "Atentamente,\nEquipo Médico"
        )
    )
    email_template_doctor = models.TextField(
        default=(
            "Estimado/a Dr. {doctor_name},\n\n"
            "Le recordamos que tiene una cita programada con el paciente {patient_name} "
            "el {appointment_date} a las {appointment_time}.\n\n"
            "Atentamente,\nEquipo Médico"
        )
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reminder_configurations"
    )

    class Meta:
        verbose_name = "Configuración de recordatorios"
        verbose_name_plural = "Configuraciones de recordatorios"

    def __str__(self):
        return f"Configuración de recordatorios ({self.hours_before} horas antes)"

class ReminderLog(models.Model):
    """Registro de recordatorios enviados"""
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name="reminders"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_to_patient = models.BooleanField(default=False)
    sent_to_doctor = models.BooleanField(default=False)
    patient_email = models.EmailField(blank=True, null=True)
    doctor_email = models.EmailField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Registro de recordatorio"
        verbose_name_plural = "Registro de recordatorios"
        
    def __str__(self):
        return f"Recordatorio para cita #{self.booking.id} enviado el {self.sent_at}"

class UserReminderPreference(models.Model):
    """Preferencias de recordatorio por usuario"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reminder_preferences"
    )
    enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    hours_before = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Preferencia de recordatorio"
        verbose_name_plural = "Preferencias de recordatorios"
        
    def __str__(self):
        return f"Preferencias de recordatorio para {self.user.username}"
