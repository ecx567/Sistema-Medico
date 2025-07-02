from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import datetime, timedelta

from .models import AuditLog, AuditSettings
from .forms import AuditFilterForm, AuditSettingsForm


@staff_member_required
def audit_dashboard(request):
    """Panel de control de auditoría para administradores"""
    # Verificar permisos
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
    
    # Obtener o crear configuración
    settings, created = AuditSettings.objects.get_or_create(
        defaults={'updated_by': request.user}
    )
    
    # Estadísticas generales
    total_logs = AuditLog.objects.count()
    login_attempts = AuditLog.objects.filter(event_type=AuditLog.LOGIN).count()
    failed_logins = AuditLog.objects.filter(
        event_type=AuditLog.LOGIN, 
        action__icontains="fallido"
    ).count()
    
    # Eventos críticos recientes
    critical_events = AuditLog.objects.filter(
        criticality__in=[AuditLog.ERROR, AuditLog.CRITICAL]
    ).order_by('-timestamp')[:10]
    
    # Eventos recientes (últimas 24 horas)
    recent_events = AuditLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=1)
    ).order_by('-timestamp')[:20]
    
    # Distribución por tipo de evento
    event_types = AuditLog.objects.values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Distribución por categoría
    categories = AuditLog.objects.values('object_category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'settings': settings,
        'total_logs': total_logs,
        'login_attempts': login_attempts,
        'failed_logins': failed_logins,
        'critical_events': critical_events,
        'recent_events': recent_events,
        'event_types': event_types,
        'categories': categories,
    }
    
    return render(request, 'audit/dashboard.html', context)


@staff_member_required
def audit_logs(request):
    """Vista para explorar y filtrar logs de auditoría"""
    # Verificar permisos
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
    
    # Inicializar filtros
    filter_form = AuditFilterForm(request.GET)
    queryset = AuditLog.objects.all()
    
    # Aplicar filtros si el formulario es válido
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # Filtro por fecha
        if data.get('start_date'):
            queryset = queryset.filter(timestamp__gte=data['start_date'])
        if data.get('end_date'):
            queryset = queryset.filter(timestamp__lte=data['end_date'])
        
        # Filtro por tipo de evento
        if data.get('event_type'):
            queryset = queryset.filter(event_type=data['event_type'])
        
        # Filtro por categoría
        if data.get('object_category'):
            queryset = queryset.filter(object_category=data['object_category'])
        
        # Filtro por criticidad
        if data.get('criticality'):
            queryset = queryset.filter(criticality=data['criticality'])
        
        # Filtro por usuario
        if data.get('user'):
            queryset = queryset.filter(user=data['user'])
        
        # Búsqueda general
        if data.get('search'):
            search_term = data['search']
            queryset = queryset.filter(
                Q(action__icontains=search_term) | 
                Q(details__icontains=search_term) |
                Q(object_repr__icontains=search_term) |
                Q(ip_address__icontains=search_term)
            )
    
    # Ordenar resultados
    queryset = queryset.order_by('-timestamp')
    
    # Paginación
    paginator = Paginator(queryset, 50)  # 50 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'filter_form': filter_form,
        'page_obj': page_obj,
    }
    
    return render(request, 'audit/logs.html', context)


@staff_member_required
def audit_settings(request):
    """Vista para configurar el sistema de auditoría"""
    # Verificar permisos
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
    
    # Obtener o crear configuración
    settings, created = AuditSettings.objects.get_or_create(
        defaults={'updated_by': request.user}
    )
    
    if request.method == 'POST':
        form = AuditSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            audit_settings = form.save(commit=False)
            audit_settings.updated_by = request.user
            audit_settings.save()
            messages.success(request, _("Configuración de auditoría actualizada correctamente"))
            return redirect('audit:settings')
    else:
        form = AuditSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    
    return render(request, 'audit/settings.html', context)
