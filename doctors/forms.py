from django import forms

from accounts.models import User
from bookings.models import Prescription
from ckeditor5.widgets import CKEditor5Widget

from core.models import Speciality
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

from django import forms
from django.core.validators import MinValueValidator
from accounts.models import Profile, User



class DoctorProfileForm(forms.ModelForm):
    """Formulario para el perfil de doctor"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'upload'}),
        help_text="Selecciona una imagen para tu perfil"
    )
    specializations = forms.ModelMultipleChoiceField(
        queryset=Speciality.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    class Meta:
        model = Profile
        fields = [
            'avatar', 'dob', 'gender', 'phone', 'address', 'city',
            'state', 'postal_code', 'country', 'about',  # cambiado 'bio' por 'about' e 'image' por 'avatar'
            'specialization', 'price_per_consultation'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_consultation': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marca los campos obligatorios
        self.fields['gender'].required = True
        self.fields['phone'].required = True
        
        # Si tenemos una instancia existente, inicializamos los campos con los valores actuales
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            
            # Configuración de especialidades
            if self.instance.specialization:
                specialties = [s.strip() for s in self.instance.specialization.split(',')]
                # Obtenemos solo las especialidades que existen
                existing_specialities = Speciality.objects.filter(name__in=specialties)
                if existing_specialities.exists():
                    self.fields['specializations'].initial = existing_specialities


class DoctorAvailabilityForm(forms.Form):
    """Formulario para configurar la disponibilidad del doctor por día de la semana"""
    # Se genera dinámicamente en la vista para cada día de la semana
    day_enabled = forms.BooleanField(required=False)
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False
    )


class DoctorPasswordChangeForm(forms.Form):
    """Formulario para cambiar la contraseña del doctor"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña actual"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nueva contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar contraseña"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('La contraseña actual es incorrecta')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden')
        
        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["symptoms", "diagnosis", "medications", "notes"]
        widgets = {
            "symptoms": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "diagnosis": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "medications": CKEditor5Widget(config_name="default"),
            "notes": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }
#
