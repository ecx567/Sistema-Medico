from django import forms
from .models import ReminderConfiguration, UserReminderPreference

class ReminderConfigurationForm(forms.ModelForm):
    """Formulario para configurar recordatorios a nivel global"""
    
    class Meta:
        model = ReminderConfiguration
        fields = [
            'hours_before', 'enabled', 'email_subject', 
            'email_template_patient', 'email_template_doctor'
        ]
        widgets = {
            'email_template_patient': forms.Textarea(attrs={'rows': 6}),
            'email_template_doctor': forms.Textarea(attrs={'rows': 6}),
        }

class UserReminderPreferenceForm(forms.ModelForm):
    """Formulario para preferencias de recordatorio por usuario"""
    
    class Meta:
        model = UserReminderPreference
        fields = ['enabled', 'email_enabled', 'hours_before']
        widgets = {
            'hours_before': forms.NumberInput(attrs={
                'placeholder': 'Usar configuración global'
            })
        }
