from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """Modelo para registrar eventos de auditoría en el sistema"""
    
    # Tipos de eventos
    LOGIN = 'login'
    LOGOUT = 'logout'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    VIEW = 'view'
    EXPORT = 'export'
    PRINT = 'print'
    ERROR = 'error'
    OTHER = 'other'
    
    EVENT_TYPES = (
        (LOGIN, _('Inicio de sesión')),
        (LOGOUT, _('Cierre de sesión')),
        (CREATE, _('Creación')),
        (UPDATE, _('Actualización')),
        (DELETE, _('Eliminación')),
        (VIEW, _('Visualización')),
        (EXPORT, _('Exportación')),
        (PRINT, _('Impresión')),
        (ERROR, _('Error')),
        (OTHER, _('Otro')),
    )
    
    # Categorías de objetos
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    APPOINTMENT = 'appointment'
    PRESCRIPTION = 'prescription'
    MEDICAL_RECORD = 'medical_record'
    REVIEW = 'review'
    USER = 'user'
    SYSTEM = 'system'
    
    OBJECT_CATEGORIES = (
        (PATIENT, _('Paciente')),
        (DOCTOR, _('Médico')),
        (APPOINTMENT, _('Cita')),
        (PRESCRIPTION, _('Receta')),
        (MEDICAL_RECORD, _('Historial médico')),
        (REVIEW, _('Reseña')),
        (USER, _('Usuario')),
        (SYSTEM, _('Sistema')),
    )
    
    # Niveles de criticidad
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'
    
    CRITICALITY_LEVELS = (
        (INFO, _('Informativo')),
        (WARNING, _('Advertencia')),
        (ERROR, _('Error')),
        (CRITICAL, _('Crítico')),
    )
    
    # Campos del modelo
    timestamp = models.DateTimeField(_('Fecha y hora'), auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='audit_logs',
        verbose_name=_('Usuario')
    )
    ip_address = models.GenericIPAddressField(_('Dirección IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    event_type = models.CharField(_('Tipo de evento'), max_length=20, choices=EVENT_TYPES)
    object_category = models.CharField(_('Categoría'), max_length=20, choices=OBJECT_CATEGORIES)
    object_id = models.CharField(_('ID del objeto'), max_length=50, blank=True)
    object_repr = models.CharField(_('Representación del objeto'), max_length=255, blank=True)
    action = models.CharField(_('Acción'), max_length=255)
    details = models.TextField(_('Detalles'), blank=True)
    criticality = models.CharField(_('Criticidad'), max_length=10, choices=CRITICALITY_LEVELS, default=INFO)
    
    class Meta:
        verbose_name = _('Registro de auditoría')
        verbose_name_plural = _('Registros de auditoría')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['event_type']),
            models.Index(fields=['object_category']),
            models.Index(fields=['criticality']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"


class AuditSettings(models.Model):
    """Configuración global para el sistema de auditoría"""
    enabled = models.BooleanField(_('Habilitado'), default=True)
    log_login_attempts = models.BooleanField(_('Registrar intentos de inicio de sesión'), default=True)
    log_data_access = models.BooleanField(_('Registrar acceso a datos'), default=True)
    log_data_changes = models.BooleanField(_('Registrar cambios en datos'), default=True)
    log_critical_operations = models.BooleanField(_('Registrar operaciones críticas'), default=True)
    retention_days = models.PositiveIntegerField(
        _('Días de retención'), 
        default=365,
        help_text=_('Número de días que se conservarán los registros antes de ser eliminados automáticamente')
    )
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_settings_updates',
        verbose_name=_('Actualizado por')
    )
    
    class Meta:
        verbose_name = _('Configuración de auditoría')
        verbose_name_plural = _('Configuraciones de auditoría')
    
    def __str__(self):
        return "Configuración de auditoría"
    
    def save(self, *args, **kwargs):
        # Aseguramos que solo exista una instancia de configuración
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)
