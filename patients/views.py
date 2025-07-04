import os
import json
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DetailView, UpdateView, TemplateView, CreateView
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest, Http404, JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.db import models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import date, datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Count, Max
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils.decorators import method_decorator
from accounts.models import User, Profile
from bookings.models import Booking
# Eliminar esta línea que causa el problema
# from bookings.forms import BookingForm
from doctors.models.general import TimeRange, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
from mixins.custom_mixins import PatientRequiredMixin
from .forms import MedicalHistoryForm, BookingForm
from accounts.decorators import AdminRequiredMixin
from patients.forms import PatientProfileForm, ChangePasswordForm, ReviewForm
from core.models import Speciality, Review
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin

# Importar el modelo de Feedback
from feedback.models import Feedback


class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = "patients/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener citas del paciente
        bookings = Booking.objects.filter(patient=self.request.user)

        # Estadísticas
        context['total_bookings'] = bookings.count()
        context['pending_bookings'] = bookings.filter(status='pending').count()
        context['completed_bookings'] = bookings.filter(status='completed').count()
        
        # Citas recientes
        context['recent_bookings'] = bookings.order_by('-booking_date')[:5]
        
        # Doctores visitados
        doctors_visited = bookings.values('doctor').distinct().count()
        context['doctors_visited'] = doctors_visited
        
        # Próxima cita
        next_booking = bookings.filter(
            appointment_date__gte=date.today(),
            status='pending'
        ).order_by('appointment_date', 'appointment_time').first()
        context['next_booking'] = next_booking
        
        return context


class PatientProfileUpdateView(PatientRequiredMixin, UpdateView):
    model = User
    form_class = PatientProfileForm
    template_name = "patients/profile-setting.html"
    success_url = reverse_lazy("patients:profile-setting")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        # Update profile
        user = form.save(commit=False)
        profile = user.profile

        # Handle profile image upload
        if self.request.FILES.get("avatar"):
            profile.image = self.request.FILES["avatar"]

        # Update profile fields
        profile_fields = [
            "dob",
            "blood_group",
            "gender",
            "phone",
            "medical_conditions",
            "allergies",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
        ]

        for field in profile_fields:
            value = self.request.POST.get(field)
            if value:
                setattr(profile, field, value)

        # Save both user and profile
        user.save()
        profile.save()

        messages.success(self.request, "Profile updated successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blood_group_choices"] = [
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("O+", "O+"),
            ("O-", "O-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ]
        return context


class AppointmentDetailView(DetailView):
    model = Booking
    template_name = "patients/appointment-detail.html"
    context_object_name = "appointment"

    def get_queryset(self):
        user = self.request.user
        # Crear un queryset base con las relaciones necesarias
        queryset = Booking.objects.select_related(
            "doctor", "doctor__profile", "patient", "patient__profile"
        )
        
        # Filtrar según el rol del usuario
        if user.role == 'doctor':
            return queryset.filter(Q(doctor=user) | Q(patient=user))
        elif user.is_staff:  # Administrador
            return queryset  # Sin filtro, puede ver todas
        else:  # Paciente
            return queryset.filter(patient=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        # Verificar si ya existe una reseña para esta cita
        from core.models import Review
        context['has_review'] = Review.objects.filter(booking=booking).exists()
        return context


class AppointmentCancelView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(
            Booking,
            pk=pk,
            patient=request.user,
            status__in=["pending", "confirmed"],
        )

        appointment.status = "cancelled"
        appointment.save()

        messages.success(request, "Appointment cancelled successfully")
        return redirect("patients:dashboard")


class AppointmentPrintView(DetailView):
    model = Booking
    template_name = "patients/appointment-print.html"
    context_object_name = "appointment"

    def get_queryset(self):
        user = self.request.user
        # Crear un queryset base con las relaciones necesarias
        queryset = Booking.objects.select_related(
            "doctor", "doctor__profile", "patient", "patient__profile"
        )
        
        # Filtrar según el rol del usuario
        if user.role == 'doctor':
            return queryset.filter(Q(doctor=user) | Q(patient=user))
        elif user.is_staff:  # Administrador
            return queryset  # Sin filtro, puede ver todas
        else:  # Paciente
            return queryset.filter(patient=user)

    def render_to_response(self, context):
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html_string = render_to_string(
            self.template_name, context, request=self.request
        )
        return HttpResponse(html_string)

class ChangePasswordView(PatientRequiredMixin, View):
    template_name = "patients/change-password.html"

    def get(self, request):
        form = ChangePasswordForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user

            if user.check_password(form.cleaned_data["old_password"]):
                user.set_password(form.cleaned_data["new_password"])
                user.save()

                # Update session to prevent logout
                update_session_auth_hash(request, user)

                messages.success(request, "Password changed successfully")
                return redirect("patients:dashboard")
            else:
                messages.error(request, "Current password is incorrect")

        return render(request, self.template_name, {"form": form})


class AddReviewView(PatientRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "patients/add_review.html"

    def form_valid(self, form):
        booking_id = self.kwargs.get("booking_id")
        booking = get_object_or_404(
            Booking, id=booking_id, patient=self.request.user
        )

        if booking.status != "completed":
            messages.error(
                self.request, "You can only review completed appointments."
            )
            return redirect("patients:appointment-detail", pk=booking_id)

        if Review.objects.filter(booking=booking).exists():
            messages.error(
                self.request, "You have already reviewed this appointment."
            )
            return redirect("patients:appointment-detail", pk=booking_id)

        form.instance.patient = self.request.user
        form.instance.doctor = booking.doctor
        form.instance.booking = booking
        messages.success(self.request, "Thank you for your review!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "patients:appointment-detail",
            kwargs={"pk": self.kwargs["booking_id"]},
        )



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


# Nueva vista para listar todos los pacientes (solo para administradores)
class PatientListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "patients/patients-list.html"
    context_object_name = "patients"
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(role="patient").select_related("profile").order_by('first_name', 'last_name')

        # Búsqueda
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) | 
                Q(email__icontains=query)
            )
        
        # Filtro por estado (con/sin visitas)
        status = self.request.GET.get('status')
        if status == 'active':
            # Pacientes con al menos una visita
            queryset = queryset.filter(patient_appointments__isnull=False).distinct()
        elif status == 'inactive':
            # Pacientes sin visitas
            queryset = queryset.filter(patient_appointments__isnull=True)

        # Ordenamiento
        sort_param = self.request.GET.get('sort', '')
        if ':' in sort_param:
            field, order = sort_param.split(':')
            
            if field == 'name':
                if order == 'asc':
                    queryset = queryset.order_by('first_name', 'last_name')
                else:
                    queryset = queryset.order_by('-first_name', '-last_name')
            elif field == 'last_visit':
                # Esto requiere una subconsulta o un enfoque diferente
                if order == 'asc':
                    queryset = queryset.annotate(
                        last_visit_date=Max('patient_appointments__appointment_date')
                    ).order_by(Coalesce('last_visit_date', date(1900, 1, 1)))
                else:
                    queryset = queryset.annotate(
                        last_visit_date=Max('patient_appointments__appointment_date')
                    ).order_by(Coalesce('last_visit_date', date(1900, 1, 1)).desc())
            elif field == 'age':
                # El ordenamiento por edad es más complejo porque se calcula
                queryset = list(queryset)
                queryset.sort(
                    key=lambda x: x.profile.age if hasattr(x.profile, 'age') and x.profile.age else 0, 
                    reverse=(order == 'desc')
                )
            elif field == 'total_paid':
                # Esto requiere agregar una anotación para el total pagado
                queryset = queryset.annotate(
                    total_paid_amount=Coalesce(
                        Sum(
                            'patient_appointments__doctor__profile__price_per_consultation', 
                            filter=Q(patient_appointments__status='completed')
                        ), 
                        0
                    )
                )
                if order == 'asc':
                    queryset = queryset.order_by('total_paid_amount')
                else:
                    queryset = queryset.order_by('-total_paid_amount')

        # Añadir campos computados para cada paciente
        for patient in queryset:
            # Obtener fecha de última visita
            latest_appointment = (
                Booking.objects.filter(patient=patient)
                .order_by("-appointment_date")
                .first()
            )
            patient.last_visit = (
                latest_appointment.appointment_date if latest_appointment else None
            )
            # Calcular total pagado
            patient.total_paid = (
                Booking.objects.filter(patient=patient, status="completed").aggregate(
                    total=models.Sum("doctor__profile__price_per_consultation")
                )["total"]
                or 0
            )
            # Calcular edad a partir de la fecha de nacimiento
            if patient.profile.dob:
                today = date.today()
                patient.profile.age = (
                    today.year
                    - patient.profile.dob.year
                    - (
                        (today.month, today.day)
                        < (patient.profile.dob.month, patient.profile.dob.day)
                    )
                )
            else:
                patient.profile.age = None

            # Obtener estadísticas de citas
            patient.total_appointments = Booking.objects.filter(patient=patient).count()
            patient.completed_appointments = Booking.objects.filter(
                patient=patient, status="completed"
            ).count()
        return queryset


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "patients/patient-detail.html"
    context_object_name = "patient"
    
    def get_queryset(self):
        return User.objects.filter(role="patient").select_related("profile")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Obtener historial de citas
        context["appointments"] = (
            Booking.objects.select_related("doctor", "doctor__profile")
            .filter(patient=patient)
            .order_by("-appointment_date", "-appointment_time")
        )
        
        # Estadísticas
        context["total_appointments"] = Booking.objects.filter(patient=patient).count()
        context["completed_appointments"] = Booking.objects.filter(
            patient=patient, status="completed"
        ).count()
        context["cancelled_appointments"] = Booking.objects.filter(
            patient=patient, status="cancelled"
        ).count()
        
        # Total pagado
        context["total_paid"] = (
            Booking.objects.filter(patient=patient, status="completed").aggregate(
                total=models.Sum("doctor__profile__price_per_consultation")
            )["total"]
            or 0
        )
        
        # Última visita
        latest_appointment = (
            Booking.objects.filter(patient=patient)
            .order_by("-appointment_date")
            .first()
        )
        context["last_visit"] = latest_appointment.appointment_date if latest_appointment else None
        
        return context


class PatientEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "patients/patient-edit.html"
    form_class = PatientProfileForm
    
    def get_queryset(self):
        return User.objects.filter(role="patient")
    
    def get_success_url(self):
        return reverse_lazy("patients:patient-detail", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        user = form.save(commit=False)
        profile = user.profile
        
        # Handle profile image upload
        if self.request.FILES.get("avatar"):
            profile.image = self.request.FILES["avatar"]
        
        # Update profile fields
        profile_fields = [
            "dob",
            "blood_group",
            "gender",
            "phone",
            "medical_conditions",
            "allergies",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
        ]

        for field in profile_fields:
            value = self.request.POST.get(field)
            if value:
                setattr(profile, field, value)
        
        # Save both user and profile
        user.save()
        profile.save()
        
        messages.success(self.request, f"Perfil de {user.get_full_name()} actualizado correctamente.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blood_group_choices"] = [
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("O+", "O+"),
            ("O-", "O-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
        ]
        return context


@login_required
def after_register_patient(request, pk):
    """Vista que se muestra después de registrar un paciente"""
    patient = get_object_or_404(User, pk=pk, role='patient')
    
    # Búsqueda de doctores
    query = request.GET.get('q', '')
    specialization = request.GET.get('specialization', '')
    
    doctors = User.objects.filter(role='doctor').select_related('profile').order_by('first_name', 'last_name')
    
    if query:
        doctors = doctors.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(profile__specialization__icontains=query)
        )
    
    if specialization:
        doctors = doctors.filter(profile__specialization__icontains=specialization)
    
    # Obtener especialidades para el filtro
    specializations = User.objects.filter(role='doctor').values_list(
        'profile__specialization', flat=True
    ).distinct().order_by('profile__specialization')

    # Paginación
    paginator = Paginator(doctors, 9)  # 9 doctores por página
    page_number = request.GET.get('page')
    doctors_page = paginator.get_page(page_number)

    return render(request, 'patients/after_register.html', {
        'patient': patient,
        'doctors': doctors_page,
        'query': query,
        'specialization': specialization,
        'specializations': specializations,
        'is_admin': request.user.is_staff,
    })


# @login_required
# def doctor_booking(request, doctor_pk, patient_pk):
#     """Vista para agendar cita con un doctor"""
#     doctor = get_object_or_404(User, pk=doctor_pk, role='doctor')
#     patient = get_object_or_404(User, pk=patient_pk, role='patient')

#     # Verificar si el doctor tiene horarios configurados
#     has_schedule = False
#     days_models = [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday]
    
#     for day_model in days_models:
#         if hasattr(doctor, day_model.__name__.lower()):
#             day_instance = getattr(doctor, day_model.__name__.lower())
#             if day_instance and day_instance.time_range.exists():
#                 has_schedule = True
#                 break
    
#     if not has_schedule:
#         return render(request, 'patients/doctor_no_schedule.html', {
#             'doctor': doctor,
#             'patient': patient,
#             'is_admin': request.user.is_staff,
#         })

#     if request.method == 'POST':
#         form = BookingForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             # Calcular costo según tipo de consulta
#             consultation_type = form.cleaned_data['consultation_type']
#             cost = 50 if consultation_type == 'normal' else 100  # Valores estándar
            
#             # Crear la cita
#             booking = Booking.objects.create(
#                 doctor=doctor,
#                 patient=patient,
#                 appointment_date=form.cleaned_data['date'],
#                 appointment_time=form.cleaned_data['time'],
#                 status='pending',
#                 notes=form.cleaned_data['reason'],
#                 consultation_type=consultation_type,
#             )

#             # Manejar archivo de historial médico si fue cargado
#             if form.cleaned_data.get('medical_history_file'):
#                 file = form.cleaned_data['medical_history_file']
#                 file_ext = os.path.splitext(file.name)[1]
#                 new_filename = f"medical_history_{patient.id}_{booking.id}{file_ext}"
                
#                 # Guardar en el directorio media
#                 file_path = f"medical_histories/{new_filename}"
#                 os.makedirs(os.path.join(settings.MEDIA_ROOT, 'medical_histories'), exist_ok=True)
                
#                 with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb+') as destination:
#                     for chunk in file.chunks():
#                         destination.write(chunk)
                
#                 booking.medical_history_file = file_path
#                 booking.save()

#             # Guardar información de historial clínico
#             if form.cleaned_data.get('medical_conditions'):
#                 if not patient.profile.medical_conditions:
#                     patient.profile.medical_conditions = form.cleaned_data['medical_conditions']
#                     patient.profile.save()
            
#             messages.success(request, "Cita agendada correctamente.")
#             return render(request, 'patients/booking_success.html', {
#                 'doctor': doctor,
#                 'patient': patient,
#                 'booking': booking,
#                 'cost': cost,
#             })
#     else:
#         form = BookingForm()

#     # Obtener horarios disponibles
#     available_slots = get_available_slots(doctor)
    
#     # Convertir a JSON para usar en JavaScript
#     available_slots_json = json.dumps(available_slots)
    
#     return render(request, 'patients/doctor_booking.html', {
#         'doctor': doctor,
#         'patient': patient,
#         'form': form,
#         'available_slots': available_slots_json,
#         'is_admin': request.user.is_staff
#     })


@login_required
def doctor_booking(request, doctor_pk, patient_pk):
    """Vista para agendar cita con un doctor"""
    doctor = get_object_or_404(User, pk=doctor_pk, role='doctor')
    patient = get_object_or_404(User, pk=patient_pk, role='patient')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            # Obtener datos del formulario
            appointment_date = form.cleaned_data['appointment_date']
            appointment_time = form.cleaned_data['appointment_time']
            consultation_type = form.cleaned_data.get('consultation_type', 'general')
            notes = form.cleaned_data.get('notes', '')
            
            # Verificar si ya existe una cita para este doctor en la fecha y hora indicadas
            existing_booking = Booking.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_booking:
                messages.error(request, "Ya existe una cita programada para este doctor en la fecha y hora seleccionadas.")
                return redirect("patients:doctor-booking", doctor_pk=doctor_pk, patient_pk=patient_pk)
            
            # Calcular costo
            cost = doctor.profile.price_per_consultation if hasattr(doctor, 'profile') and doctor.profile.price_per_consultation else 50.00
            
            # Crear la cita
            booking = Booking.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                notes=notes,
                status='pending',
                consultation_type=consultation_type,
            )
            
            # Guardar archivo de historial médico si se proporcionó
            if 'medical_history_file' in request.FILES:
                booking.medical_history_file = request.FILES['medical_history_file']
                booking.save()
            
            # Actualizar información médica del paciente si se proporcionó
            if form.cleaned_data.get('medical_conditions'):
                if not patient.profile.medical_conditions:
                    patient.profile.medical_conditions = form.cleaned_data['medical_conditions']
                    patient.profile.save()
            
            messages.success(request, "Cita agendada correctamente.")
            return render(request, 'patients/booking_success.html', {
                'doctor': doctor,
                'patient': patient,
                'booking': booking,
                'cost': cost,
            })
    else:
        form = BookingForm()

    # Obtener horarios disponibles
    available_slots = get_available_slots(doctor)
    
    return render(request, 'patients/doctor_booking.html', {
        'doctor': doctor,
        'patient': patient,
        'form': form,
        'available_slots': available_slots,
        'is_admin': request.user.is_staff
    })



def get_available_slots(doctor):
    """Obtiene los slots disponibles para un doctor"""
    # Obtener todos los horarios del doctor
    days_models = [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday]
    available_slots = {}
    
    # Obtener citas existentes para este doctor
    today = date.today()
    end_date = today + timedelta(days=30)  # Mostrar disponibilidad para los próximos 30 días
    
    existing_bookings = Booking.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        appointment_date__lte=end_date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_date', 'appointment_time')
    
    # Convertir a set para búsqueda rápida
    booked_slots = {(booking_date.strftime('%Y-%m-%d'), booking_time.strftime('%H:%M:%S')) for booking_date, booking_time in existing_bookings}
    
    # Para cada día en el rango de 30 días
    current_date = today
    while current_date <= end_date:
        day_name = current_date.strftime('%A')  # Nombre del día en inglés (Monday, Tuesday, etc)
        day_model = next((model for model in days_models if model.__name__ == day_name), None)
        
        if day_model and hasattr(doctor, day_model.__name__.lower()):
            day_instance = getattr(doctor, day_model.__name__.lower())
            
            if day_instance and day_instance.time_range.exists():
                slots_for_day = []
                
                for time_range in day_instance.time_range.all():
                    # Usar los atributos start y end (no start_time, end_time)
                    start_time = datetime.combine(today, time_range.start)
                    end_time = datetime.combine(today, time_range.end)
                    
                    # Generar slots de 30 minutos
                    current_slot = start_time
                    while current_slot < end_time:
                        slot_time = current_slot.time()
                        slot_time_str = slot_time.strftime('%H:%M:%S')
                        current_date_str = current_date.strftime('%Y-%m-%d')

                        # Verificar si este slot ya está reservado
                        if (current_date_str, slot_time_str) not in booked_slots:
                            slots_for_day.append({
                                'time': slot_time.strftime('%H:%M'),
                                'timestamp': slot_time_str
                            })
                        
                        # Avanzar 30 minutos
                        current_slot += timedelta(minutes=30)
                
                if slots_for_day:
                    date_str = current_date.strftime('%Y-%m-%d')
                    available_slots[date_str] = {
                        'date_display': current_date.strftime('%d/%m/%Y'),
                        'day_name': day_name,
                        'slots': slots_for_day
                    }
        
        # Avanzar al siguiente día
        current_date += timedelta(days=1)
    
    return available_slots


@login_required
def get_available_slots_api(request, doctor_pk):
    """API para obtener slots disponibles en formato JSON"""
    doctor = get_object_or_404(User, pk=doctor_pk, role='doctor')
    slots = get_available_slots(doctor)
    return JsonResponse(slots)
