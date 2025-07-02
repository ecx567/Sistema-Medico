from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security.audit'
    verbose_name = 'Auditoría del Sistema'
    
    def ready(self):
        import security.audit.signals
