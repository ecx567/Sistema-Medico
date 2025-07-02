from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from functools import wraps


def patient_required(view_func):
    """Decorator para vistas que requieren un usuario paciente"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'is_patient') and request.user.is_patient:
            return view_func(request, *args, **kwargs)
        messages.error(request, _("Solo los pacientes pueden acceder a esta página."))
        return redirect('home')
    return _wrapped_view


def doctor_required(view_func):
    """Decorator para vistas que requieren un usuario médico"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'is_doctor') and request.user.is_doctor:
            return view_func(request, *args, **kwargs)
        messages.error(request, _("Solo los médicos pueden acceder a esta página."))
        return redirect('home')
    return _wrapped_view


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(
                request, "You are not authorized to access this page."
            )
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

# class AdminRequiredMixin:
#     """Mixin para vistas basadas en clases que requieren un usuario administrador"""
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated or not request.user.is_staff:
#             messages.error(request, _("Solo los administradores pueden acceder a esta página."))
#             return redirect('home')
#         return super().dispatch(request, *args, **kwargs)
