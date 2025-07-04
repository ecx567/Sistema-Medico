from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


class PatientRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and user is patient"""

    permission_denied_message = "You are not authorized to view this page"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != "patient":
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and user is patient"""

    permission_denied_message = "You are not authorized to view this page"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # if request.user.role != "doctor":
        #     return self.handle_no_permission()
        # return super().dispatch(request, *args, **kwargs)
        if not (request.user.role == "doctor" or request.user.is_staff):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
