from django.core.management.base import BaseCommand
from django.utils import timezone
from reminders.services import ReminderService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Envía recordatorios de citas programadas'

    def handle(self, *args, **options):
        """
        Ejecuta el envío de recordatorios para las citas próximas
        """
        self.stdout.write(
            self.style.SUCCESS(f"Iniciando envío de recordatorios a {timezone.now()}")
        )
        
        # Obtener citas que necesitan recordatorio
        pending_bookings = ReminderService.get_pending_reminders()
        
        if not pending_bookings:
            self.stdout.write(
                self.style.SUCCESS("No hay recordatorios pendientes para enviar")
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f"Encontrados {pending_bookings.count()} recordatorios pendientes")
        )
        
        # Procesar cada cita
        success_count = 0
        error_count = 0
        
        for booking in pending_bookings:
            try:
                result = ReminderService.send_reminder(booking)
                if result:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Recordatorio enviado para cita #{booking.id}")
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error al enviar recordatorio para cita #{booking.id}")
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ Excepción al procesar cita #{booking.id}: {str(e)}")
                )
                logger.exception(f"Error procesando recordatorio para cita #{booking.id}")
        
        # Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso completado: {success_count} enviados, {error_count} errores"
            )
        )
