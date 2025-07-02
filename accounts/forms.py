from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class DoctorRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(DoctorRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "First name"
        self.fields["last_name"].label = "Last name"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm your password"

        self.fields["first_name"].widget.attrs.update(
            {
                "placeholder": "Enter first name",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "placeholder": "Enter last name",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Enter email",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Enter password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Confirm your password",
            }
        )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        error_messages = {
            "first_name": {
                "required": "First name is required",
                "max_length": "Name is too long",
            },
            "last_name": {
                "required": "Last name is required",
                "max_length": "Last Name is too long",
            },
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "doctor"
        if commit:
            user.save()
        return user


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "patient"
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Enter Username"}
        )
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Enter Password"}
        )

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if password and password:
            self.user = authenticate(username=username, password=password)

            if self.user is None:
                raise forms.ValidationError("Username or password is incorrect.")
            if not self.user.check_password(password):
                raise forms.ValidationError("Username or password is incorrect.")
            if not self.user.is_active:
                raise forms.ValidationError("User is not active.")

        return super(UserLoginForm, self).clean(*args, **kwargs)

    def get_user(self):
        return self.user



#########


# Agregar al final del archivo

class QuickPatientRegistrationForm(forms.ModelForm):
    """Formulario simplificado para registro rápido de pacientes"""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
        max_length=30,
        required=True,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
        max_length=30,
        required=True,
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        max_length=30,
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo Electrónico"}),
        max_length=255,
        required=True,
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de teléfono"}),
        max_length=15,
        required=False,
    )
    address = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección"}),
        max_length=255,
        required=False,
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ciudad"}),
        max_length=100,
        required=False,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = "patient"
        
        if commit:
            user.save()
            # Crear o actualizar perfil
            profile, created = user.profile, False
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                from accounts.models import Profile
                profile = Profile(user=user)
                
            profile.phone = self.cleaned_data.get("phone_number", "")
            profile.address = self.cleaned_data.get("address", "")
            profile.city = self.cleaned_data.get("city", "")
            profile.save()
            
        return user


class QuickDoctorRegistrationForm(forms.ModelForm):
    """Formulario simplificado para registro rápido de médicos"""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
        max_length=30,
        required=True,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
        max_length=30,
        required=True,
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        max_length=30,
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo Electrónico"}),
        max_length=255,
        required=True,
    )
    specialization = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Especialización"}),
        max_length=100,
        required=True,
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de teléfono"}),
        max_length=15,
        required=False,
    )
    price_per_consultation = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Precio por consulta"}),
        max_digits=10,
        decimal_places=2,
        required=False,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = "doctor"
        
        if commit:
            user.save()
            # Crear o actualizar perfil
            profile, created = user.profile, False
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                from accounts.models import Profile
                profile = Profile(user=user)
                
            profile.specialization = self.cleaned_data.get("specialization", "")
            profile.phone = self.cleaned_data.get("phone_number", "")
            profile.price_per_consultation = self.cleaned_data.get("price_per_consultation", 0)
            profile.save()
            
        return user
