from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Avg
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail  # Añadir esta importación
from django.conf import settings  # Añadir esta importación
from textblob import TextBlob 

from .models import Feedback, FeedbackResponse
from .forms import FeedbackForm , FeedbackResponseForm
from bookings.models import Booking

@login_required
def leave_feedback(request, booking_id):
    """Vista para dejar retroalimentación después de una cita"""
    booking = get_object_or_404(
        Booking, 
        id=booking_id, 
        patient=request.user,
        status='completed'
    )
    
    # Verificar si ya existe retroalimentación para esta cita
    if hasattr(booking, 'feedback'):
        messages.info(request, "Ya has dejado retroalimentación para esta cita.")
        return redirect('patient:dashboard')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = request.user
            feedback.doctor = booking.doctor
            feedback.booking = booking

            # Análisis de sentimiento con TextBlob
            if feedback.comment:
                analysis = TextBlob(feedback.comment)
                feedback.sentiment_score = analysis.sentiment.polarity
                
                # Clasificar el sentimiento
                if feedback.sentiment_score > 0.3:
                    feedback.sentiment = "positivo"
                elif feedback.sentiment_score < -0.3:
                    feedback.sentiment = "negativo"
                else:
                    feedback.sentiment = "neutral"


            feedback.save()
            
            messages.success(request, "¡Gracias por tu retroalimentación!")
            return redirect('patient:dashboard')
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/leave_feedback.html', {
        'form': form,
        'booking': booking
    })

@login_required
def doctor_feedbacks(request):
    """Vista para que los médicos vean sus retroalimentaciones"""
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Acceso denegado")
    
    feedbacks = Feedback.objects.filter(
        doctor=request.user,
        is_approved=True
    ).order_by('-created_at')
    
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0
    
    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'feedback/doctor_feedbacks.html', {
        'page_obj': page_obj,
        'avg_rating': avg_rating,
        'total_feedbacks': feedbacks.count()
    })

@login_required
def admin_feedbacks(request):
    """Vista para administradores para moderar retroalimentaciones"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Acceso denegado")
    
    # Filtrar por estado (aprobado/pendiente/rechazado)
    filter_status = request.GET.get('status')
    
    feedbacks = Feedback.objects.all().order_by('-created_at')
    if filter_status == 'pending':
        feedbacks = feedbacks.filter(is_approved=False)
    elif filter_status == 'approved':
        feedbacks = feedbacks.filter(is_approved=True)
    
    paginator = Paginator(feedbacks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'feedback/admin_feedbacks.html', {
        'page_obj': page_obj,
        'filter_status': filter_status or 'all'
    })

@require_POST
@login_required
def approve_feedback(request, feedback_id):
    """Aprobar retroalimentación (solo admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.is_approved = True
    feedback.save()

    # Enviar notificación por email al paciente
    send_mail(
        'Tu retroalimentación ha sido aprobada',
        f'Hola {feedback.patient.get_full_name()},\n\nTu retroalimentación para la cita con Dr. {feedback.doctor.get_full_name()} ha sido aprobada y ya es visible en el sistema.\n\nGracias por compartir tu experiencia.\n\nEquipo de Doccure',
        settings.DEFAULT_FROM_EMAIL,
        [feedback.patient.email],
        fail_silently=False,
    )
    
    # Enviar notificación por email al médico
    send_mail(
        'Nueva retroalimentación aprobada',
        f'Hola Dr. {feedback.doctor.get_full_name()},\n\nUna nueva retroalimentación de {feedback.patient.get_full_name()} ha sido aprobada y ya es visible en tu perfil.\n\nEquipo de Doccure',
        settings.DEFAULT_FROM_EMAIL,
        [feedback.doctor.email],
        fail_silently=False,
    )
    
    return JsonResponse({'success': True})

@require_POST
@login_required
def reject_feedback(request, feedback_id):
    """Rechazar retroalimentación (solo admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.is_approved = False
    feedback.save()
    
    return JsonResponse({'success': True})

@login_required
def respond_to_feedback(request, feedback_id):
    """Vista para que los médicos respondan a retroalimentaciones"""
    feedback = get_object_or_404(Feedback, id=feedback_id, doctor=request.user, is_approved=True)
    
    # Verificar si ya existe una respuesta
    try:
        response = FeedbackResponse.objects.get(feedback=feedback)
        messages.info(request, "Ya has respondido a esta retroalimentación.")
        return redirect('feedback:doctor-feedbacks')
    except FeedbackResponse.DoesNotExist:
        response = None
    
    if request.method == 'POST':
        form = FeedbackResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.feedback = feedback
            response.doctor = request.user
            response.save()
            
            # Notificar al paciente por email
            send_mail(
                'El médico ha respondido a tu retroalimentación',
                f'Hola {feedback.patient.get_full_name()},\n\nEl Dr. {feedback.doctor.get_full_name()} ha respondido a tu retroalimentación. Ingresa a tu cuenta para ver la respuesta.\n\nEquipo de Doccure',
                settings.DEFAULT_FROM_EMAIL,
                [feedback.patient.email],
                fail_silently=False,
            )
            
            messages.success(request, "Tu respuesta ha sido enviada correctamente.")
            return redirect('feedback:doctor-feedbacks')
    else:
        form = FeedbackResponseForm()

    return render(request, 'feedback/respond_to_feedback.html', {
        'form': form,
        'feedback': feedback
    })

    
