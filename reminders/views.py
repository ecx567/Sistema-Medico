from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone

from .models import ReminderConfiguration, ReminderLog, UserReminderPreference
from .forms import ReminderConfigurationForm, UserReminderPreferenceForm
from .services import ReminderService

@staff_member_required
def reminder_settings(request):
    """Vista para administrar la configuración de recordatorios"""
    # Obtener o crear configuración global
    config, created = ReminderConfiguration.objects.get_or_create(
        pk=1,
        defaults={
            'updated_by': request.user
        }
    )
    
    if request.method == 'POST':
        form = ReminderConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.updated_by = request.user
            config.save()
            messages.success(request, "Configuración de recordatorios actualizada correctamente")
            return redirect('reminders:settings')
    else:
        form = ReminderConfigurationForm(instance=config)
    
    return render(request, 'reminders/settings.html', {
        'form': form,
        'config': config,
    })

@staff_member_required
def reminder_history(request):
    """Vista para ver el historial de recordatorios enviados"""
    # Filtros
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status = request.GET.get('status')
    
    # Consulta base
    reminders = ReminderLog.objects.select_related(
        'booking', 'booking__patient', 'booking__doctor'
    ).order_by('-sent_at')
    
    # Aplicar filtros
    if from_date:
        reminders = reminders.filter(sent_at__date__gte=from_date)
    if to_date:
        reminders = reminders.filter(sent_at__date__lte=to_date)
    if status == 'success':
        reminders = reminders.filter(sent_to_patient=True, sent_to_doctor=True)
    elif status == 'partial':
        reminders = reminders.filter(
            (models.Q(sent_to_patient=True) & models.Q(sent_to_doctor=False)) |
            (models.Q(sent_to_patient=False) & models.Q(sent_to_doctor=True))
        )
    elif status == 'failed':
        reminders = reminders.filter(sent_to_patient=False, sent_to_doctor=False)
    
    # Paginación
    paginator = Paginator(reminders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reminders/history.html', {
        'page_obj': page_obj,
        'filters': {
            'from_date': from_date,
            'to_date': to_date,
            'status': status,
        }
    })

@staff_member_required
def send_test_reminder(request, booking_id):
    """Envía un recordatorio de prueba para una cita específica"""
    from bookings.models import Booking
    booking = get_object_or_404(Booking, pk=booking_id)
    
    success = ReminderService.send_reminder(booking)
    
    if success:
        messages.success(request, f"Recordatorio de prueba enviado correctamente para la cita #{booking_id}")
    else:
        messages.error(request, f"Error al enviar recordatorio de prueba para la cita #{booking_id}")
    
    # Redirigir a la vista de detalles de la cita
    if request.user.role == 'DOCTOR':
        return redirect('doctors:appointment-detail', pk=booking_id)
    elif request.user.role == 'ADMIN':
        return redirect('admin:bookings_booking_change', object_id=booking_id)
    else:
        return redirect('reminders:history')

@login_required
def user_reminder_preferences(request):
    """Vista para que los usuarios ajusten sus preferencias de recordatorio"""
    # Obtener o crear preferencias
    preferences, created = UserReminderPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        form = UserReminderPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferencias de recordatorio actualizadas correctamente")
            
            # Redirigir según el rol del usuario
            if request.user.role == 'DOCTOR':
                return redirect('doctors:profile-settings')
            else:
                return redirect('patients:profile-settings')
    else:
        form = UserReminderPreferenceForm(instance=preferences)
    
    return render(request, 'reminders/user_preferences.html', {
        'form': form,
        'preferences': preferences,
    })
