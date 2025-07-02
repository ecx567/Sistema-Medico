from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import ReminderConfiguration, ReminderLog
from bookings.models import Booking

class ReminderService:
    """Servicio para gestionar recordatorios de citas"""
    
    @staticmethod
    def get_pending_reminders():
        """
        Obtiene las citas que requieren recordatorio
        """
        # Obtener la configuración de recordatorios actual
        config = ReminderConfiguration.objects.first()
        if not config or not config.enabled:
            return []
        
        # Calcular la fecha/hora para recordatorios
        target_time = timezone.now() + timedelta(hours=config.hours_before)
        
        # Encontrar citas que necesitan recordatorio
        # 1. Citas en estado 'confirmed' o 'pending'
        # 2. Citas que están programadas para aproximadamente config.hours_before horas desde ahora
        # 3. Citas que aún no han recibido recordatorio
        bookings = Booking.objects.filter(
            status__in=['confirmed', 'pending'],
            appointment_date=target_time.date(),
        ).exclude(
            reminders__isnull=False  # Excluir citas que ya tienen recordatorios
        )
        
        # Filtrar por hora aproximada (considerando ±30 minutos)
        lower_time = (target_time - timedelta(minutes=30)).time()
        upper_time = (target_time + timedelta(minutes=30)).time()
        
        if lower_time < upper_time:
            bookings = bookings.filter(
                appointment_time__gte=lower_time,
                appointment_time__lte=upper_time
            )
        else:  # Si cruza la medianoche
            bookings = bookings.filter(
                appointment_time__gte=lower_time
            ) | bookings.filter(
                appointment_time__lte=upper_time
            )
            
        return bookings
    
    @staticmethod
    def send_reminder(booking):
        """
        Envía recordatorios para una cita específica
        """
        config = ReminderConfiguration.objects.first()
        if not config:
            return False
            
        patient = booking.patient
        doctor = booking.doctor
        
        # Crear registro de recordatorio
        reminder_log = ReminderLog.objects.create(
            booking=booking,
            patient_email=patient.email,
            doctor_email=doctor.email
        )
        
        # Formato de fecha y hora para los mensajes
        appointment_date = booking.appointment_date.strftime('%d/%m/%Y')
        appointment_time = booking.appointment_time.strftime('%H:%M')
        
        success = True
        error_messages = []
        
        # Enviar email al paciente
        if patient.email and patient.reminder_preferences.enabled if hasattr(patient, 'reminder_preferences') else True:
            try:
                patient_message = config.email_template_patient.format(
                    patient_name=patient.get_full_name(),
                    doctor_name=doctor.get_full_name(),
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
                
                send_mail(
                    config.email_subject,
                    patient_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [patient.email],
                    fail_silently=False,
                )
                reminder_log.sent_to_patient = True
            except Exception as e:
                success = False
                error_messages.append(f"Error al enviar al paciente: {str(e)}")
        
        # Enviar email al doctor
        if doctor.email and doctor.reminder_preferences.enabled if hasattr(doctor, 'reminder_preferences') else True:
            try:
                doctor_message = config.email_template_doctor.format(
                    patient_name=patient.get_full_name(),
                    doctor_name=doctor.get_full_name(),
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
                
                send_mail(
                    config.email_subject,
                    doctor_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [doctor.email],
                    fail_silently=False,
                )
                reminder_log.sent_to_doctor = True
            except Exception as e:
                success = False
                error_messages.append(f"Error al enviar al doctor: {str(e)}")
        
        # Actualizar el registro con errores si los hubo
        if error_messages:
            reminder_log.error_message = "\n".join(error_messages)
        
        reminder_log.save()
        return success
