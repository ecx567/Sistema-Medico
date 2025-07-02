from django import forms

from accounts.models import User
from bookings.models import Prescription
from ckeditor5.widgets import CKEditor5Widget

from core.models import Speciality
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"


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
