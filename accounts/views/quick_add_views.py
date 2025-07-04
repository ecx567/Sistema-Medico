from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from accounts.models import User
from accounts.forms import QuickPatientRegistrationForm, QuickDoctorRegistrationForm


class QuickAddPatientView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para agregar pacientes rápidamente desde la interfaz"""
    model = User
    form_class = QuickPatientRegistrationForm
    template_name = "accounts/quick_add_patient.html"
    #success_url = reverse_lazy("patients:dashboard")
    #template_name = "accounts/quick_add_patient.html"
    
    def test_func(self):
        # Solo admin o pacientes pueden agregar pacientes
        return self.request.user.is_staff or self.request.user.role == 'patient'
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"El paciente {user.get_full_name()} ha sido registrado correctamente.")
        #return super().form_valid(form)
        return redirect('patients:after-register', pk=user.pk)


class QuickAddDoctorView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para agregar médicos rápidamente desde la interfaz"""
    model = User
    form_class = QuickDoctorRegistrationForm
    template_name = "accounts/quick_add_doctor.html"
    #success_url = reverse_lazy("doctors:dashboard")
    def test_func(self):
        # Solo admin o doctores pueden agregar doctores
        return self.request.user.is_staff or self.request.user.role == 'doctor'
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"El doctor {user.get_full_name()} ha sido registrado correctamente.")
        #return super().form_valid(form)
        return redirect('patients:after-register', pk=user.pk)
