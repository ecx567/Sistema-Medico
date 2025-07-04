import sys
import json
from datetime import datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.http import (
    HttpRequest,
    HttpResponse,
    Http404,
    HttpResponsePermanentRedirect,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic import (
    ListView,
    DetailView,
    View,
    CreateView,
    UpdateView,
)
from django.views.generic.base import TemplateView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from bookings.models import Booking, Prescription
from core.decorators import user_is_doctor
from doctors.forms import DoctorProfileForm, PrescriptionForm, DoctorPasswordChangeForm
from doctors.models import Experience
from doctors.models.general import *
from doctors.serializers import (
    EducationSerializer,
    ExperienceSerializer,
    RegistrationNumberSerializer,
    SpecializationSerializer,
)
from mixins.custom_mixins import DoctorRequiredMixin
from patients.forms import ChangePasswordForm
from utils.htmx import render_toast_message_for_api
from accounts.models import User, Profile
from bookings.models import Booking

# Importar el modelo de Feedback
from feedback.models import Feedback
from django.db.models import Avg, Count, Q

from core.models import Speciality, TimeRange
from doctors.models import Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday


days = {
    0: Sunday,
    1: Monday,
    2: Tuesday,
    3: Wednesday,
    4: Thursday,
    5: Friday,
    6: Saturday,
}


class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = "doctors/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

         # Obtener citas del doctor
        bookings = Booking.objects.filter(doctor=doctor)

        # Get appointment counts
        context["total_patients"] = (
            Booking.objects.filter(doctor=self.request.user)
            .values("patient")
            .distinct()
            .count()
        )

        context["today_patients"] = Booking.objects.filter(
            doctor=self.request.user, appointment_date=today
        ).count()

        context["total_appointments"] = Booking.objects.filter(
            doctor=self.request.user
        ).count()

        # Get upcoming appointments
        context["upcoming_appointments"] = (
            Booking.objects.select_related("patient", "patient__profile")
            .filter(
                doctor=self.request.user,
                appointment_date__gte=today,
                status__in=["pending", "confirmed"],
            )
            .order_by("appointment_date", "appointment_time")[:10]
        )

        # Get today's appointments
        context["today_appointments"] = (
            Booking.objects.select_related("patient", "patient__profile")
            .filter(doctor=self.request.user, appointment_date=today)
            .order_by("appointment_time")
        )

        return context


def convert_to_24_hour_format(time_str):
    if time_str == "00:00 AM":
        time_str = "12:00 AM"
    return datetime.strptime(time_str, "%I:%M %p").time()


@login_required
@user_is_doctor
def schedule_timings(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        data = request.POST
        for i in range(7):
            if data.get(f"day_{i}", None):
                start_times = data.getlist(f"start_time_{i}", default=[])
                end_times = data.getlist(f"end_time_{i}", default=[])
                for index in range(len(start_times)):
                    start = convert_to_24_hour_format(start_times[index])
                    end = convert_to_24_hour_format(end_times[index])
                    time_range, time_created = TimeRange.objects.get_or_create(
                        start=start, end=end
                    )
                    day, created = days[i].objects.get_or_create(
                        user=request.user
                    )
                    ranges = day.time_range
                    if time_range.id not in list(
                        ranges.values_list("id", flat=True)
                    ):
                        day.time_range.add(time_range)

        return HttpResponsePermanentRedirect(
            reverse_lazy("doctors:schedule-timings")
        )

    return render(request, "doctors/schedule-timings.html")


# class DoctorProfileUpdateView(DoctorRequiredMixin, generic.UpdateView):
#     model = User
#     template_name = "doctors/profile-settings.html"
#     form_class = DoctorProfileForm

#     def get_object(self, queryset=None):
#         return self.request.user

class DoctorProfileUpdateView(DoctorRequiredMixin, UpdateView):
    """Vista para actualizar el perfil del doctor"""
    model = Profile
    form_class = DoctorProfileForm
    template_name = "doctors/profile-setting.html"
    
    def get_object(self, queryset=None):
        doctor_id = self.kwargs.get('doctor_id')
        if self.request.user.is_staff and doctor_id:
            user = get_object_or_404(User, id=doctor_id, role='doctor')
            return user.profile
        return self.request.user.profile

    def get_success_url(self):
        doctor_id = self.kwargs.get('doctor_id')
        if self.request.user.is_staff and doctor_id:
            return reverse_lazy('doctors:after-register', kwargs={'pk': doctor_id})
        return reverse_lazy("doctors:profile-setting")

    def form_valid(self, form):
        profile = form.save(commit=False)
        user = profile.user
        
        user.first_name = self.request.POST.get('first_name', user.first_name)
        user.last_name = self.request.POST.get('last_name', user.last_name)
        
        if self.request.FILES.get('avatar'):
            profile.image = self.request.FILES['avatar']
        
        specializations = self.request.POST.getlist('specializations')
        if specializations:
            profile.specialization = ", ".join(specializations)
        
        user.save()
        profile.save()
        
        messages.success(self.request, "Perfil actualizado correctamente")
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object().user
        context['specialities'] = Speciality.objects.all()
        if self.object.specialization:
            context['doctor_specialities'] = [s.strip() for s in self.object.specialization.split(',')]
        else:
            context['doctor_specialities'] = []
        return context
    
class DoctorProfileView(DetailView):
    context_object_name = "doctor"
    model = User
    slug_url_kwarg = "username"
    slug_field = "username"
    template_name = "doctors/profile.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)
        queryset = queryset.select_related("profile").prefetch_related(
            "educations",
            "experiences",
            "sunday__time_range",
            "monday__time_range",
            "tuesday__time_range",
            "wednesday__time_range",
            "thursday__time_range",
            "friday__time_range",
            "saturday__time_range",
        )

        try:
            obj = queryset.get(
                **{self.slug_field: slug, "role": User.RoleChoices.DOCTOR}
            )
        except User.DoesNotExist:
            raise Http404(f"No doctor found matching the username")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object

        # Get current day name
        current_day = datetime.now().strftime("%A")

        # Prepare business hours
        business_hours = {
            "Sunday": (
                doctor.sunday.time_range.all()
                if hasattr(doctor, "sunday")
                else []
            ),
            "Monday": (
                doctor.monday.time_range.all()
                if hasattr(doctor, "monday")
                else []
            ),
            "Tuesday": (
                doctor.tuesday.time_range.all()
                if hasattr(doctor, "tuesday")
                else []
            ),
            "Wednesday": (
                doctor.wednesday.time_range.all()
                if hasattr(doctor, "wednesday")
                else []
            ),
            "Thursday": (
                doctor.thursday.time_range.all()
                if hasattr(doctor, "thursday")
                else []
            ),
            "Friday": (
                doctor.friday.time_range.all()
                if hasattr(doctor, "friday")
                else []
            ),
            "Saturday": (
                doctor.saturday.time_range.all()
                if hasattr(doctor, "saturday")
                else []
            ),
        }

        # --- Feedback integration ---
        feedbacks = Feedback.objects.filter(
            doctor=doctor,
            is_approved=True
        ).order_by('-created_at')

        feedback_stats = feedbacks.aggregate(
            avg_rating=Avg('rating'),
            count=Count('id'),
            five_star=Count('id', filter=Q(rating=5)),
            four_star=Count('id', filter=Q(rating=4)),
            three_star=Count('id', filter=Q(rating=3)),
            two_star=Count('id', filter=Q(rating=2)),
            one_star=Count('id', filter=Q(rating=1))
        )

        total = feedback_stats['count'] or 1
        feedback_stats.update({
            'five_star_percent': (feedback_stats['five_star'] / total) * 100,
            'four_star_percent': (feedback_stats['four_star'] / total) * 100,
            'three_star_percent': (feedback_stats['three_star'] / total) * 100,
            'two_star_percent': (feedback_stats['two_star'] / total) * 100,
            'one_star_percent': (feedback_stats['one_star'] / total) * 100,
        })

        recent_feedbacks = feedbacks[:5]

        context.update(
            {
                "current_day": current_day,
                "business_hours": business_hours,
                "reviews": doctor.reviews_received.select_related(
                    "patient", "patient__profile"
                ).order_by("-created_at"),
                "feedbacks": recent_feedbacks,
                "feedback_stats": feedback_stats,
            }
        )

        return context


class UpdateEducationAPIView(DoctorRequiredMixin, UpdateAPIView):
    queryset = Experience.objects.all()
    serializer_class = EducationSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        data = request.POST
        ids = data.getlist("id", default=[])
        degrees = data.getlist("degree", default=[])
        colleges = data.getlist("college", default=[])
        years = data.getlist("year_of_completion", default=[])
        for i in range(len(degrees)):
            try:
                instance = self.request.user.educations.get(id=ids[i])
                degree = degrees[i]
                college = colleges[i]
                year_of_completion = years[i]
                serializer = self.get_serializer(
                    instance,
                    data={
                        "degree": degree,
                        "college": college,
                        "year_of_completion": year_of_completion,
                    },
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except:
                degree = degrees[i]
                college = colleges[i]
                year_of_completion = years[i]
                serializer = self.get_serializer(
                    data={
                        "degree": degree,
                        "college": college,
                        "year_of_completion": year_of_completion,
                    }
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

        response = Response({"success": True})
        response.headers["HX-Trigger"] = json.dumps(
            {
                "show-toast": {
                    "level": "success",
                    "title": "Education",
                    "message": "Successfully updated",
                }
            }
        )
        return response


class UpdateExperienceAPIView(DoctorRequiredMixin, UpdateAPIView):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        data = request.POST
        ids = data.getlist("id", default=[])
        institutions = data.getlist("institution", default=[])
        from_years = data.getlist("from_year", default=[])
        to_years = data.getlist("to_year", default=[])
        designations = data.getlist("designation", default=[])

        for i in range(len(institutions)):
            try:
                instance = self.request.user.educations.get(id=ids[i])
                institution = institutions[i]
                from_year = from_years[i]
                to_year = to_years[i]
                designation = designations[i]
                serializer = self.get_serializer(
                    instance,
                    data={
                        "institution": institution,
                        "from_year": from_year,
                        "to_year": to_year,
                        "designation": designation,
                    },
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except:
                institution = institutions[i]
                from_year = from_years[i]
                to_year = to_years[i]
                designation = designations[i]
                serializer = self.get_serializer(
                    data={
                        "institution": institution,
                        "from_year": from_year,
                        "to_year": to_year,
                        "designation": designation,
                    }
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

        return render_toast_message_for_api(
            "Experience", "Updated successfully", "success"
        )


class UpdateRegistrationNumberAPIView(DoctorRequiredMixin, UpdateAPIView):
    serializer_class = RegistrationNumberSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        data = request.POST
        serializer = self.get_serializer(instance=request.user, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return render_toast_message_for_api(
            "BM&DC number", "Updated successfully", "success"
        )


class UpdateSpecializationAPIView(DoctorRequiredMixin, UpdateAPIView):
    serializer_class = SpecializationSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.POST
        specialist = data.get("specialist")
        instance.profile.specialization = specialist
        instance.profile.save()

        return render_toast_message_for_api(
            "Specialization", "Updated successfully", "success"
        )


class DoctorsListView(ListView):
    model = User
    context_object_name = "doctors"
    template_name = "doctors/list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = self.model.objects.filter(
            role=User.RoleChoices.DOCTOR, is_superuser=False, is_active=True
        ).select_related("profile")

        # Handle search query
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(profile__specialization__icontains=search_query)
                | Q(profile__city__icontains=search_query)
            )

        # Handle gender filter
        gender = self.request.GET.getlist("gender")
        if gender:
            queryset = queryset.filter(profile__gender__in=gender)

        # Handle specialization filter
        specializations = self.request.GET.getlist("specialization")
        if specializations:
            queryset = queryset.filter(
                profile__specialization__in=specializations
            )

        # Handle sorting
        sort_by = self.request.GET.get("sort")
        if sort_by:
            if sort_by == "price_low":
                queryset = queryset.order_by("profile__price_per_consultation")
            elif sort_by == "price_high":
                queryset = queryset.order_by(
                    "-profile__price_per_consultation"
                )
            elif sort_by == "rating":
                queryset = queryset.order_by("-rating")
            elif sort_by == "experience":
                queryset = queryset.order_by("-profile__experience")
        else:
            queryset = queryset.order_by("-pk")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search query to context
        context["search_query"] = self.request.GET.get("q")

        # Add unique specializations to context
        specializations = (
            User.objects.filter(role=User.RoleChoices.DOCTOR, is_active=True)
            .exclude(profile__specialization__isnull=True)
            .values_list("profile__specialization", flat=True)
            .distinct()
        )

        context["specializations"] = sorted(
            list(filter(None, specializations))
        )

        return context


class AppointmentListView(DoctorRequiredMixin, ListView):
    model = Booking
    context_object_name = "appointments"
    template_name = "doctors/appointments.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            self.model.objects.select_related(
                "doctor", "doctor__profile", "patient", "patient__profile"
            )
            .filter(doctor=self.request.user)
            .order_by("-appointment_date", "-appointment_time")
        )


class AppointmentDetailView(DoctorRequiredMixin, DetailView):
    model = Booking
    template_name = "doctors/appointment-detail.html"
    context_object_name = "appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object.patient

        # Get patient's appointment history with this doctor
        context["patient_history"] = (
            Booking.objects.select_related("doctor", "doctor__profile")
            .filter(
                doctor=self.request.user,
                patient=patient,
                appointment_date__lt=self.object.appointment_date,
            )
            .order_by("-appointment_date", "-appointment_time")
        )

        # Get total visits count
        context["total_visits"] = Booking.objects.filter(
            doctor=self.request.user, patient=patient, status="completed"
        ).count()

        return context


class AppointmentActionView(DoctorRequiredMixin, View):
    def post(self, request, pk, action):
        appointment = get_object_or_404(
            Booking,
            pk=pk,
            doctor=request.user,
            status__in=["pending", "confirmed"],
        )

        if action == "accept":
            appointment.status = "confirmed"
            messages.success(request, "Appointment confirmed successfully")
        elif action == "cancel":
            appointment.status = "cancelled"
            messages.success(request, "Appointment cancelled successfully")
        elif action == "completed":
            appointment.status = "completed"
            messages.success(
                request, "Appointment marked as completed successfully"
            )

        appointment.save()
        return redirect("doctors:dashboard")


class MyPatientsView(DoctorRequiredMixin, ListView):
    template_name = "doctors/my-patients.html"
    context_object_name = "patients"

    def get_queryset(self):
        # Get unique patients who have appointments with this doctor
        return (
            User.objects.filter(
                patient_appointments__doctor=self.request.user, role="patient"
            )
            .distinct()
            .select_related("profile")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get appointment counts for each patient
        patient_stats = {}
        for patient in context["patients"]:
            stats = Booking.objects.filter(
                doctor=self.request.user, patient=patient
            ).aggregate(
                total_appointments=Count("id"),
                completed_appointments=Count(
                    "id", filter=Q(status="completed")
                ),
            )
            patient_stats[patient.id] = stats
        context["patient_stats"] = patient_stats
        return context


class AppointmentHistoryView(DoctorRequiredMixin, ListView):
    model = Booking
    template_name = "doctors/appointment-history.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return (
            self.model.objects.select_related("patient", "patient__profile")
            .filter(
                doctor=self.request.user, patient_id=self.kwargs["patient_id"]
            )
            .order_by("-appointment_date", "-appointment_time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = get_object_or_404(
            User.objects.select_related("profile"),
            id=self.kwargs["patient_id"],
            role="patient",
        )
        return context


class DoctorChangePasswordView(DoctorRequiredMixin, View):
    template_name = "doctors/change-password.html"

    def get(self, request, *args, **kwargs):
        return render(
            request, self.template_name, {"form": ChangePasswordForm()}
        )

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user

            if user.check_password(form.cleaned_data["old_password"]):
                user.set_password(form.cleaned_data["new_password"])
                user.save()

                # Update session to prevent logout
                update_session_auth_hash(request, user)

                messages.success(request, "Password changed successfully")
                return redirect("doctors:dashboard")
            else:
                messages.error(request, "Current password is incorrect")

        return render(request, self.template_name, {"form": form})


class PrescriptionCreateView(DoctorRequiredMixin, CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = "doctors/add_prescription.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get("booking_id")
        context["booking"] = get_object_or_404(
            Booking, id=booking_id, doctor=self.request.user
        )
        return context

    def form_valid(self, form):
        booking_id = self.kwargs.get("booking_id")
        booking = get_object_or_404(
            Booking, id=booking_id, doctor=self.request.user
        )

        if booking.status != "completed":
            messages.error(
                self.request,
                "Can only add prescription for completed appointments",
            )
            return redirect("doctors:appointment-detail", pk=booking_id)

        form.instance.booking = booking
        form.instance.doctor = self.request.user
        form.instance.patient = booking.patient
        messages.success(self.request, "Prescription added successfully")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "doctors:appointment-detail",
            kwargs={"pk": self.kwargs["booking_id"]},
        )


class PrescriptionDetailView(DoctorRequiredMixin, DetailView):
    model = Prescription
    template_name = "doctors/prescription_detail.html"
    context_object_name = "prescription"

    def get_queryset(self):
        # Only allow doctors to view prescriptions they wrote
        return Prescription.objects.filter(
            doctor=self.request.user
        ).select_related(
            "doctor",
            "doctor__profile",
            "patient",
            "patient__profile",
            "booking",
        )


#####

@login_required
def after_register_doctor(request, pk):
    """Vista que se muestra después de registrar un doctor"""
    doctor = get_object_or_404(User, pk=pk, role='doctor')
    
    # Obtener todos los doctores con estadísticas
    doctors = User.objects.filter(role='doctor').select_related('profile')
    
    for doc in doctors:
        # Contar pacientes únicos
        doc.patients_count = Booking.objects.filter(doctor=doc).values('patient').distinct().count()
        
        # Contar citas totales
        doc.appointments_count = Booking.objects.filter(doctor=doc).count()
        # Contar citas pendientes
        doc.pending_appointments = Booking.objects.filter(doctor=doc, status='pending').count()
        # Contar citas completadas
        doc.completed_appointments = Booking.objects.filter(doctor=doc, status='completed').count()
    
    # Obtener citas pendientes para este doctor
    pending_appointments = Booking.objects.filter(
        doctor=doctor,
        status='pending'
    ).select_related('patient', 'patient__profile')
    
    return render(request, 'doctors/after_register.html', {
        'doctor': doctor,
        'doctors': doctors,
        'pending_appointments': pending_appointments,
        'is_admin': request.user.is_staff,
    })

# @login_required
# def doctor_appointment_action(request, appointment_id, action):
#     """Acción sobre una cita (aceptar/rechazar/completar)"""
#     if request.method != 'POST':
#         return redirect('doctors:dashboard')
    
#     appointment = get_object_or_404(
#         Booking,
#         id=appointment_id,
#         doctor=request.user
#     )
    
#     if action == 'accept':
#         appointment.status = 'confirmed'
#         messages.success(request, 'Cita confirmada correctamente')
#     elif action == 'reject':
#         appointment.status = 'cancelled'
#         messages.success(request, 'Cita rechazada correctamente')
#     elif action == 'complete':
#         appointment.status = 'completed'
#         messages.success(request, 'Cita marcada como completada correctamente')
    
#     appointment.save()

#     # Redireccionar a la página actual (after-register o dashboard)
#     referer = request.META.get('HTTP_REFERER')
#     if referer:
#         return redirect(referer)
    
#     return redirect('doctors:dashboard')

@login_required
def doctor_appointment_action(request, appointment_id, action):
    """Acción sobre una cita (aceptar/rechazar/completar)"""
    if request.method != 'POST':
        return redirect('doctors:dashboard')
    
    appointment = get_object_or_404(
        Booking,
        id=appointment_id,
        doctor=request.user
    )
    
    if action == 'accept':
        appointment.status = 'confirmed'
        messages.success(request, 'Cita confirmada correctamente')
    elif action == 'reject':
        appointment.status = 'cancelled'
        messages.success(request, 'Cita rechazada correctamente')
    elif action == 'complete':
        appointment.status = 'completed'
        messages.success(request, 'Cita marcada como completada correctamente')
    
    appointment.save()

    # Redireccionar a la página actual (after-register o dashboard)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    
    return redirect('doctors:dashboard')

# Agregar esta vista para la página de éxito de cita
class AppointmentSuccessView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "patients/appointment-success.html"
    context_object_name = "appointment"
    pk_url_kwarg = 'booking_id'

    def get_queryset(self):
        return Booking.objects.select_related(
            "doctor", "doctor__profile", "patient", "patient__profile"
        ).filter(patient=self.request.user)



####

# Añadir esta clase a las vistas existentes

# Añadir esta clase a las vistas existentes

class ScheduleTimingsView(DoctorRequiredMixin, TemplateView):
    """Vista para gestionar los horarios del doctor"""
    template_name = "doctors/schedule-timings.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el doctor actual
        doctor = self.request.user
        
        # Obtener configuración de días de la semana
        context["monday"] = doctor.monday if hasattr(doctor, 'monday') else None
        context["tuesday"] = doctor.tuesday if hasattr(doctor, 'tuesday') else None
        context["wednesday"] = doctor.wednesday if hasattr(doctor, 'wednesday') else None
        context["thursday"] = doctor.thursday if hasattr(doctor, 'thursday') else None
        context["friday"] = doctor.friday if hasattr(doctor, 'friday') else None
        context["saturday"] = doctor.saturday if hasattr(doctor, 'saturday') else None
        context["sunday"] = doctor.sunday if hasattr(doctor, 'sunday') else None
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Procesar la actualización de horarios
        days_list = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        days_models = [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday]
        days_dict = dict(zip(days_list, days_models))
        
        for day_name in days_list:
            day_enabled = request.POST.get(f"{day_name}_enabled") == "on"
            day_model_class = days_dict[day_name]
            
            # Obtener o crear el modelo para este día
            try:
                day_model = getattr(request.user, day_name)
            except:
                day_model = None
            
            if day_enabled:
                if not day_model:
                    # Crear el modelo si no existe
                    day_model = day_model_class.objects.create(user=request.user)
                    setattr(request.user, day_name, day_model)
                
                # Limpiar rangos de tiempo existentes
                if hasattr(day_model, 'time_range'):
                    day_model.time_range.all().delete()
                
                # Obtener rangos de tiempo para este día
                slots = int(request.POST.get(f"{day_name}_slots", 0))
                
                for i in range(slots):
                    start_time = request.POST.get(f"{day_name}_start_{i}")
                    end_time = request.POST.get(f"{day_name}_end_{i}")
                    
                    if start_time and end_time:
                        time_range = TimeRange.objects.create(
                            start=start_time,
                            end=end_time
                        )
                        day_model.time_range.add(time_range)
            else:
                # Si el día está deshabilitado y existe el modelo, eliminar sus rangos
                if day_model and hasattr(day_model, 'time_range'):
                    day_model.time_range.all().delete()
        
        messages.success(request, "Horarios actualizados correctamente")
        return redirect("doctors:schedule-timings")

