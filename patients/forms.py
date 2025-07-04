from django import forms
from datetime import date
from accounts.models import User
from core.models import Review
from django.utils.translation import gettext_lazy as _
from .models import MedicalRecord, MedicalDiagnosis

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password

class PatientProfileForm(forms.ModelForm):
    """
    Patent profile update form
    """

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    avatar = forms.ImageField(required=False)
    dob = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    blood_group = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select Blood Group"),
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("O+", "O+"),
            ("O-", "O-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ],
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select Gender"),
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
    )
    phone = forms.CharField(required=False)
    medical_conditions = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "List any chronic conditions, surgeries, etc.",
            }
        ),
    )
    allergies = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "List any allergies to medications, food, etc.",
            }
        ),
    )
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)
    postal_code = forms.CharField(required=False)
    country = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Add phone number validation if needed
            if not phone.isdigit():
                raise forms.ValidationError(
                    "Phone number should contain only digits"
                )
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if postal_code:
            # Add postal code validation if needed
            if not postal_code.isdigit():
                raise forms.ValidationError(
                    "Postal code should contain only digits"
                )
        return postal_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Current Password"}
        )
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New Password"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm New Password",
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("The new passwords don't match")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "review"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your review here...",
                }
            ),
        }

##################

class MedicalRecordForm(forms.ModelForm):
    """Formulario para crear/editar el historial médico"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'allergies', 'medications', 'chronic_diseases', 
            'previous_surgeries', 'family_history', 
            'blood_type', 'height', 'weight', 'notes'
        ]
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'previous_surgeries': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'family_history': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class MedicalDiagnosisForm(forms.ModelForm):
    """Formulario para agregar/editar diagnósticos médicos"""
    
    class Meta:
        model = MedicalDiagnosis
        fields = ['diagnosis', 'diagnosis_date', 'treatment', 'notes']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosis_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'treatment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


   
##

#####

class BookingForm(forms.Form):
    """Formulario para agendar citas"""
    reason = forms.CharField(
        label="Motivo de la consulta",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=True
    )
    
    consultation_type = forms.ChoiceField(
        label="Tipo de consulta",
        choices=[
            ('normal', 'Consulta General ($50)'),
            ('specialty', 'Consulta por Especialidad ($100)')
        ],
        widget=forms.RadioSelect,
        required=True
    )
    
    date = forms.DateField(
        label="Fecha",
        widget=forms.HiddenInput(),
        required=True
    )
    
    time = forms.TimeField(
        label="Hora",
        widget=forms.HiddenInput(),
        required=True
    )
    medical_conditions = forms.CharField(
        label="Condiciones médicas o enfermedades",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    
    medical_history_file = forms.FileField(
        label="Subir historial clínico (PDF o imagen)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Puede subir un archivo PDF o una imagen de su historial clínico"
    )
    def clean_medical_history_file(self):
        file = self.cleaned_data.get('medical_history_file')
        if file:
            # Validar el tamaño del archivo (10 MB máximo)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo no puede superar los 10 MB")
            
            # Validar la extensión del archivo
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Solo se permiten archivos PDF o imágenes (jpg, jpeg, png)")
        
        return file

class MedicalHistoryForm(forms.Form):
    """Formulario para historial médico"""
    medical_conditions = forms.CharField(
        label="Condiciones médicas",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    allergies = forms.CharField(
        label="Alergias",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    current_medications = forms.CharField(
        label="Medicamentos actuales",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    past_surgeries = forms.CharField(
        label="Cirugías anteriores",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    family_history = forms.CharField(
        label="Historial familiar",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )

################

# class QuickPatientRegistrationForm(forms.ModelForm):
#     """Formulario simplificado para registro rápido de pacientes"""
#     first_name = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
#         max_length=30,
#         required=True,
#     )
#     last_name = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
#         max_length=30,
#         required=True,
#     )
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
#         max_length=30,
#         required=True,
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo Electrónico"}),
#         max_length=255,
#         required=True,
#     )
#     phone_number = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de teléfono"}),
#         max_length=15,
#         required=False,
#     )
#     address = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección"}),
#         max_length=255,
#         required=False,
#     )
#     city = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ciudad"}),
#         max_length=100,
#         required=False,
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
#         required=True,
#     )
#     class Meta:
#         model = User
#         fields = ["first_name", "last_name", "username", "email", "password"]

#     def clean_username(self):
#         username = self.cleaned_data["username"]
#         if User.objects.filter(username=username).exists():
#             raise forms.ValidationError("Este nombre de usuario ya está en uso")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Este correo electrónico ya está registrado")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         user.role = "patient"

#         if commit:
#             user.save()
#             # Crear o actualizar perfil
#             profile, created = user.profile, False
#             if hasattr(user, 'profile'):
#                 profile = user.profile
#             else:
#                 from accounts.models import Profile
#                 profile = Profile(user=user)
                
#             profile.phone = self.cleaned_data.get("phone_number", "")
#             profile.address = self.cleaned_data.get("address", "")
#             profile.city = self.cleaned_data.get("city", "")
#             profile.save()
            
#         return user

# class QuickDoctorRegistrationForm(forms.ModelForm):
#     """Formulario simplificado para registro rápido de médicos"""
#     first_name = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
#         max_length=30,
#         required=True,
#     )
#     last_name = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
#         max_length=30,
#         required=True,
#     )
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
#         max_length=30,
#         required=True,
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo Electrónico"}),
#         max_length=255,
#         required=True,
#     )
#     specialization = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Especialización"}),
#         max_length=100,
#         required=True,
#     )
#     phone_number = forms.CharField(
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de teléfono"}),
#         max_length=15,
#         required=False,
#     )
#     price_per_consultation = forms.DecimalField(
#         widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Precio por consulta"}),
#         max_digits=10,
#         decimal_places=2,
#         required=False,
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
#         required=True,
#     )

#     class Meta:
#         model = User
#         fields = ["first_name", "last_name", "username", "email", "password"]

#     def clean_username(self):
#         username = self.cleaned_data["username"]
#         if User.objects.filter(username=username).exists():
#             raise forms.ValidationError("Este nombre de usuario ya está en uso")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data["email"]
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Este correo electrónico ya está registrado")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         user.role = "doctor"

#         if commit:
#             user.save()
#             # Crear o actualizar perfil
#             profile, created = user.profile, False
#             if hasattr(user, 'profile'):
#                 profile = user.profile
#             else:
#                 from accounts.models import Profile
#                 profile = Profile(user=user)
                
#             profile.specialization = self.cleaned_data.get("specialization", "")
#             profile.phone = self.cleaned_data.get("phone_number", "")
#             profile.price_per_consultation = self.cleaned_data.get("price_per_consultation", 0)
#             profile.save()
            
#         return user
    


    
