from django.contrib import admin
from .models import AuditLog, AuditSettings
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_type', 'user_display', 'object_category', 'object_repr', 'action', 'criticality_badge', 'ip_address')
    list_filter = ('event_type', 'object_category', 'criticality', 'timestamp')
    search_fields = ('user__username', 'user__email', 'action', 'details', 'object_repr', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'ip_address', 'user_agent', 'event_type', 'object_category', 
                      'object_id', 'object_repr', 'action', 'details', 'criticality')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (_('Información temporal'), {
            'fields': ('timestamp', 'ip_address', 'user_agent')
        }),
        (_('Usuario'), {
            'fields': ('user',)
        }),
        (_('Evento'), {
            'fields': ('event_type', 'action', 'criticality')
        }),
        (_('Objeto afectado'), {
            'fields': ('object_category', 'object_id', 'object_repr')
        }),
        (_('Detalles adicionales'), {
            'fields': ('details',)
        }),
    )
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return "Sistema"
    user_display.short_description = _('Usuario')
    
    def criticality_badge(self, obj):
        colors = {
            'info': 'green',
            'warning': 'orange',
            'error': 'red',
            'critical': 'purple'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>',
            colors.get(obj.criticality, 'gray'),
            obj.get_criticality_display()
        )
    criticality_badge.short_description = _('Criticidad')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditSettings)
class AuditSettingsAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'log_login_attempts', 'log_data_access', 'log_data_changes', 
                   'log_critical_operations', 'retention_days', 'updated_at', 'updated_by')
    readonly_fields = ('updated_at', 'updated_by')
    
    fieldsets = (
        (_('Estado'), {
            'fields': ('enabled',)
        }),
        (_('Configuración de registro'), {
            'fields': ('log_login_attempts', 'log_data_access', 'log_data_changes', 'log_critical_operations')
        }),
        (_('Retención de datos'), {
            'fields': ('retention_days',)
        }),
        (_('Metadatos'), {
            'fields': ('updated_at', 'updated_by')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Solo permitir añadir si no hay instancia existente
        return not AuditSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False
