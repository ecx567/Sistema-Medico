from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
import json

from .models import AuditLog, AuditSettings
from accounts.models import User
from bookings.models import Booking, Prescription
from patients.models import MedicalRecord, MedicalDiagnosis
from core.models import Review


def get_client_ip(request):
    """Obtiene la dirección IP del cliente desde la solicitud"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtiene el user agent del cliente desde la solicitud"""
    return request.META.get('HTTP_USER_AGENT', '')


def should_log_event(event_type):
    """Determina si un tipo de evento debe ser registrado según la configuración"""
    try:
        settings = AuditSettings.objects.first()
        if not settings or not settings.enabled:
            return False
            
        if event_type in [AuditLog.LOGIN, AuditLog.LOGOUT]:
            return settings.log_login_attempts
        elif event_type in [AuditLog.VIEW]:
            return settings.log_data_access
        elif event_type in [AuditLog.CREATE, AuditLog.UPDATE, AuditLog.DELETE]:
            return settings.log_data_changes
        elif event_type in [AuditLog.ERROR, AuditLog.CRITICAL]:
            return settings.log_critical_operations
        return True
    except:
        # Si hay algún error, mejor registrar por defecto
        return True


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra inicios de sesión exitosos"""
    if not should_log_event(AuditLog.LOGIN):
        return
        
    AuditLog.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        event_type=AuditLog.LOGIN,
        object_category=AuditLog.USER,
        object_id=str(user.id),
        object_repr=user.username,
        action=_("Inicio de sesión exitoso"),
        criticality=AuditLog.INFO
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registra cierres de sesión"""
    if not user or not should_log_event(AuditLog.LOGOUT):
        return
        
    AuditLog.objects.create(
        user=user,
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
        event_type=AuditLog.LOGOUT,
        object_category=AuditLog.USER,
        object_id=str(user.id),
        object_repr=user.username,
        action=_("Cierre de sesión"),
        criticality=AuditLog.INFO
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Registra intentos fallidos de inicio de sesión"""
    if not should_log_event(AuditLog.LOGIN):
        return
        
    # Extraer el nombre de usuario de las credenciales
    username = credentials.get('username', 'desconocido')
    
    AuditLog.objects.create(
        user=None,  # Usuario desconocido o no autenticado
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
        event_type=AuditLog.LOGIN,
        object_category=AuditLog.USER,
        object_repr=username,
        action=_("Intento fallido de inicio de sesión"),
        details=json.dumps({'username': username}),
        criticality=AuditLog.WARNING
    )


# Monitoreo de cambios en entidades críticas
@receiver(post_save, sender=MedicalRecord)
def log_medical_record_changes(sender, instance, created, **kwargs):
    """Registra cambios en historiales médicos"""
    if not should_log_event(AuditLog.CREATE if created else AuditLog.UPDATE):
        return
        
    AuditLog.objects.create(
        user=instance.created_by,
        event_type=AuditLog.CREATE if created else AuditLog.UPDATE,
        object_category=AuditLog.MEDICAL_RECORD,
        object_id=str(instance.id),
        object_repr=f"Historial médico de {instance.patient}",
        action=_("Creación de historial médico") if created else _("Actualización de historial médico"),
        criticality=AuditLog.INFO if created else AuditLog.WARNING
    )


@receiver(post_save, sender=Prescription)
def log_prescription_changes(sender, instance, created, **kwargs):
    """Registra cambios en recetas médicas"""
    if not should_log_event(AuditLog.CREATE if created else AuditLog.UPDATE):
        return
        
    AuditLog.objects.create(
        user=instance.doctor,  # Asumiendo que doctor es un User
        event_type=AuditLog.CREATE if created else AuditLog.UPDATE,
        object_category=AuditLog.PRESCRIPTION,
        object_id=str(instance.id),
        object_repr=f"Receta para {instance.patient}",
        action=_("Creación de receta") if created else _("Actualización de receta"),
        criticality=AuditLog.WARNING
    )


# Función para registrar manualmente eventos
def register_audit_event(request, event_type, object_category, object_id=None, 
                        object_repr='', action='', details='', criticality=AuditLog.INFO):
    """
    Registra manualmente un evento de auditoría
    
    Args:
        request: Solicitud HTTP actual
        event_type: Tipo de evento (usar constantes de AuditLog)
        object_category: Categoría del objeto (usar constantes de AuditLog)
        object_id: ID del objeto (opcional)
        object_repr: Representación textual del objeto
        action: Descripción de la acción
        details: Detalles adicionales (string o dict que se convertirá a JSON)
        criticality: Nivel de criticidad (usar constantes de AuditLog)
    """
    if not should_log_event(event_type):
        return
        
    # Convertir details a JSON si es un diccionario
    if isinstance(details, dict):
        details = json.dumps(details)
        
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        event_type=event_type,
        object_category=object_category,
        object_id=str(object_id) if object_id else '',
        object_repr=object_repr,
        action=action,
        details=details,
        criticality=criticality
    )
