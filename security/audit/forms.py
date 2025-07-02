from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AuditSettings, AuditLog
from accounts.models import User


class AuditSettingsForm(forms.ModelForm):
    """Formulario para la configuración de auditoría"""
    
    class Meta:
        model = AuditSettings
        fields = ['enabled', 'log_login_attempts', 'log_data_access', 
                 'log_data_changes', 'log_critical_operations', 'retention_days']
        widgets = {
            'retention_days': forms.NumberInput(attrs={'min': 30, 'max': 3650})
        }
        

class AuditFilterForm(forms.Form):
    """Formulario para filtrar los registros de auditoría"""
    
    start_date = forms.DateTimeField(
        label=_('Fecha inicial'),
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    end_date = forms.DateTimeField(
        label=_('Fecha final'),
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    event_type = forms.ChoiceField(
        label=_('Tipo de evento'),
        choices=[('', '-- Todos --')] + list(AuditLog.EVENT_TYPES),
        required=False
    )
    
    object_category = forms.ChoiceField(
        label=_('Categoría'),
        choices=[('', '-- Todas --')] + list(AuditLog.OBJECT_CATEGORIES),
        required=False
    )
    
    criticality = forms.ChoiceField(
        label=_('Criticidad'),
        choices=[('', '-- Todas --')] + list(AuditLog.CRITICALITY_LEVELS),
        required=False
    )
    
    user = forms.ModelChoiceField(
        label=_('Usuario'),
        queryset=User.objects.all(),
        required=False
    )
    
    search = forms.CharField(
        label=_('Búsqueda'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Buscar en detalles, acción, IP...')})
    )
