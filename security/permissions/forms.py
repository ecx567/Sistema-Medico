from django import forms
from django.contrib.auth.models import Group
from .models import Module, Permission, GroupModulePermission


class PermissionManagementForm(forms.Form):
    """Formulario para la gestión de permisos por grupo y módulo"""
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Grupo",
        empty_label="Seleccione un Grupo",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    module = forms.ModelChoiceField(
        queryset=Module.objects.filter(is_active=True),
        label="Módulo",
        empty_label="Seleccione un Módulo",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        permissions_data = kwargs.pop('permissions_data', None)
        super().__init__(*args, **kwargs)
        
        if permissions_data:
            # Agregar campos dinámicos para cada permiso
            for perm_id, perm_data in permissions_data.items():
                self.fields[f'perm_{perm_id}'] = forms.BooleanField(
                    required=False,
                    label=perm_data['name'],
                    initial=perm_data['is_active'],
                    help_text=perm_data['description']
                )
