import os
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View,ListView, DetailView, UpdateView, TemplateView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.conf import settings
from django.views.generic.base import TemplateView
from django import forms
from accounts.models import User, Profile
from core.models import Speciality, Review
from bookings.models import Booking
from doctors.models.general import TimeRange, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
from doctors.models.general import TimeRange
from mixins.custom_mixins import PatientRequiredMixin
from .models import Booking
from datetime import datetime, timedelta


class BookingView(LoginRequiredMixin, View):
    template_name = "bookings/booking.html"

    def get_week_dates(self):
        """Get the next 7 days starting from today"""
        today = datetime.now().date()
        week_dates = []
        for i in range(7):
            date = today + timedelta(days=i)
            week_dates.append(
                {
                    "date": date,
                    "day": date.strftime("%a"),
                    "day_num": date.strftime("%d"),
                    "month": date.strftime("%b"),
                    "year": date.strftime("%Y"),
                    "full_date": date.strftime("%Y-%m-%d"),
                }
            )
        return week_dates

    def get_available_slots(self, doctor, date):
        """Get available time slots for a specific date"""
        #available_slots = {}
        day_name = date.strftime("%A").lower()
        day_schedule = getattr(doctor, day_name, None)

        if not day_schedule:
            return []

        time_slots = []
        for time_range in day_schedule.time_range.all():
            # Convert time range to slots (e.g., 30-minute intervals)
            current_time = datetime.combine(date, time_range.start)
            end_time = datetime.combine(date, time_range.end)

            while current_time < end_time:
                # Check if slot is already booked
                is_booked = doctor.appointments.filter(
                    appointment_date=date, appointment_time=current_time.time()
                ).exists()

                if not is_booked:
                    time_slots.append(
                        {
                            "time": current_time.time(),
                            "formatted_time": current_time.strftime(
                                "%I:%M %p"
                            ),
                        }
                    )
                current_time += timedelta(minutes=30)

        return time_slots

    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            doctor = (
                User.objects.select_related("profile")
                .prefetch_related(
                    "sunday__time_range",
                    "monday__time_range",
                    "tuesday__time_range",
                    "wednesday__time_range",
                    "thursday__time_range",
                    "friday__time_range",
                    "saturday__time_range",
                    "appointments",
                )
                .get(
                    username=kwargs["username"],
                    role=User.RoleChoices.DOCTOR,
                    is_active=True,
                )
            )
        except User.DoesNotExist:
            raise Http404("Doctor not found")

        # Get week dates
        week_dates = self.get_week_dates()
        schedule = {}
        for date_info in week_dates:
            date_ = datetime.strptime(date_info["full_date"], "%Y-%m-%d").date()
            schedule[date_info["full_date"]] = self.get_available_slots(
                doctor, date_
            )
        
        

        # Get available slots for each day
        schedule = {}
        for date_info in week_dates:
            date = datetime.strptime(date_info["full_date"], "%Y-%m-%d").date()
            schedule[date_info["full_date"]] = self.get_available_slots(
                doctor, date
            )

        context = {
            "doctor": doctor,
            "week_dates": week_dates,
            "schedule": schedule,
            "selected_date": request.GET.get(
                "date", week_dates[0]["full_date"]
            ),
        }

        return render(request, self.template_name, context)


class BookingCreateView(LoginRequiredMixin, View):
    template_name = "bookings/booking.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, username):
        doctor = get_object_or_404(
            User, username=username, role=User.RoleChoices.DOCTOR
        )

        # Get form data
        date = request.POST.get("selected_date")
        time = request.POST.get("selected_time")

        if not date or not time:
            messages.error(
                request, "Please select both date and time for the appointment"
            )
            return redirect("bookings:doctor-booking-view", username=username)

        try:
            # Convert string inputs to proper date/time objects
            appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
            appointment_time = datetime.strptime(time, "%H:%M").time()

            # Create the booking
            booking = Booking.objects.create(
                doctor=doctor,
                patient=request.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
            )

            messages.success(request, "Appointment booked successfully!")
            return redirect("bookings:booking-success", booking_id=booking.id)

        except ValueError:
            messages.error(request, "Invalid date or time format")
        except Exception as e:
            messages.error(request, str(e))

        return redirect("bookings:doctor-booking-view", username=username)

    
    

class BookingSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "bookings/booking-success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = Booking.objects.get(id=kwargs["booking_id"])
        return context


class BookingInvoiceView(LoginRequiredMixin, TemplateView):
    template_name = "bookings/booking-invoice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(
            Booking.objects.select_related(
                "doctor", "doctor__profile", "patient", "patient__profile"
            ),
            id=kwargs["booking_id"],
        )

        # Ensure user can only view their own bookings
        if not (
            self.request.user == booking.patient
            or self.request.user == booking.doctor
        ):
            raise Http404("Not found")

        context["booking"] = booking
        context["issued_date"] = booking.booking_date.strftime("%d/%m/%Y")

        # Calculate invoice amounts
        consultation_fee = booking.doctor.profile.price_per_consultation
        context["subtotal"] = consultation_fee
        context["total"] = (
            consultation_fee  # Add any additional fees/discounts here
        )

        return context


class BookingListView(LoginRequiredMixin, View):
    template_name = "bookings/booking-list.html"
    
    def get(self, request: HttpRequest, *args, **kwargs):
        # Get all bookings for the logged-in user
        if request.user.role == User.RoleChoices.DOCTOR:
            bookings = Booking.objects.filter(doctor=request.user)
        else:
            bookings = Booking.objects.filter(patient=request.user)
            
        # Prefetch related data to avoid N+1 queries
        bookings = bookings.select_related(
            'doctor', 
            'doctor__profile',
            'patient', 
            'patient__profile'
        ).order_by('-appointment_date', '-appointment_time')
        
        context = {
            'bookings': bookings,
        }
        
        return render(request, self.template_name, context)


####

# Formulario para agendar citas
class BookingForm(forms.Form):
    reason = forms.CharField(
        label="Motivo de la cita",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
    consultation_type = forms.ChoiceField(
        label="Tipo de consulta",
        choices=[('normal', 'Consulta Normal'), ('specialty', 'Consulta Especialidad')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    time = forms.TimeField(
        label="Hora",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        required=True
    )
    medical_conditions = forms.CharField(
        label="Condiciones médicas",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    "Solo se permiten archivos PDF o imágenes (jpg, jpeg, png)"
                )
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("El archivo no debe superar los 5MB")
        return file

@login_required
def after_register_patient(request, pk):
    """Vista que se muestra después de registrar un paciente"""
    patient = get_object_or_404(User, pk=pk, role='patient')
    
    # Búsqueda de doctores
    query = request.GET.get('q', '')
    specialization = request.GET.get('specialization', '')
    
    doctors = User.objects.filter(role='doctor').select_related('profile')
    
    if query:
        doctors = doctors.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(profile__specialization__icontains=query)
        )

    if specialization:
        doctors = doctors.filter(profile__specialization__icontains=specialization)
    
    # Obtener especialidades para el filtro
    specialities = Speciality.objects.all()
    
    return render(request, 'patients/after_register.html', {
        'patient': patient,
        'doctors': doctors,
        'query': query,
        'specialization': specialization,
        'specialities': specialities,
    })

@login_required
def doctor_booking(request, doctor_pk, patient_pk):
    """Vista para agendar cita con un doctor"""
    doctor = get_object_or_404(User, pk=doctor_pk, role='doctor')
    patient = get_object_or_404(User, pk=patient_pk, role='patient')
    
    # Verificar si el doctor tiene horarios configurados
    horarios = TimeRange.objects.filter(doctor=doctor)
    
    if not horarios.exists():
        return render(request, 'patients/doctor_no_schedule.html', {
            'doctor': doctor,
            'patient': patient,
            'is_admin': request.user.is_staff
        })

    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            # Determinar el costo según el tipo de consulta
            consultation_type = form.cleaned_data['consultation_type']
            cost = 50 if consultation_type == 'normal' else 100  # Valores estándar
            
            # Crear la cita
            booking = Booking.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=form.cleaned_data['date'],
                appointment_time=form.cleaned_data['time'],
                status='pending',
                notes=form.cleaned_data['reason'],
                consultation_type=consultation_type,
            )

            # Manejar archivo de historial médico si fue cargado
            if form.cleaned_data['medical_history_file']:
                file = form.cleaned_data['medical_history_file']
                file_ext = os.path.splitext(file.name)[1]
                new_filename = f"medical_history_{patient.id}_{booking.id}{file_ext}"
                
                # Guardar en el directorio media
                file_path = f"medical_histories/{new_filename}"
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'medical_histories'), exist_ok=True)
                
                with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                booking.medical_history_file = file_path
                booking.save()

            # Guardar información de historial clínico
            if form.cleaned_data['medical_conditions']:
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
    time_ranges = TimeRange.objects.filter(doctor=doctor)
    
    if not time_ranges.exists():
        return {}
    
    # Obtener citas existentes para este doctor
    today = datetime.now().date()
    end_date = today + timedelta(days=30)  # Mostrar disponibilidad para los próximos 30 días
    
    existing_bookings = Booking.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        appointment_date__lte=end_date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_date', 'appointment_time')
    
    # Crear un diccionario para almacenar los slots por día
    available_slots = {}
    
    # Para cada día en el rango de 30 días
    current_date = today
    while current_date <= end_date:
        day_name = current_date.strftime('%A').lower()  # Nombre del día en inglés

        # Buscar rangos de tiempo para este día
        day_ranges = time_ranges.filter(day=day_name)
        
        if day_ranges.exists():
            # Si hay horarios para este día, generar slots
            slots = []
            
            for time_range in day_ranges:
                start_time = time_range.start_time
                end_time = time_range.end_time
                
                # Generar slots de 30 minutos
                current_time = start_time
                while current_time < end_time:
                    # Verificar si este slot ya está reservado
                    is_booked = (current_date, current_time) in existing_bookings
                    
                    if not is_booked:
                        slots.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'time': current_time.strftime('%H:%M')
                        })
                    
                    # Avanzar 30 minutos
                    current_time_dt = datetime.combine(today, current_time)
                    current_time_dt += timedelta(minutes=30)
                    current_time = current_time_dt.time()
            
            # Si hay slots disponibles para este día, agregarlos al diccionario
            if slots:
                day_display = current_date.strftime('%d/%m/%Y')
                available_slots[day_display] = slots
        
        # Avanzar al siguiente día
        current_date += timedelta(days=1)
    
    return available_slots


    
