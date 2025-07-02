from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import datetime, timedelta

from .services import AnalyticsService
from .models import Report, SavedDashboard
from .serializers import ReportSerializer, SavedDashboardSerializer

# API Views para consumo por el frontend
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_stats_api(request):
    """API para estadísticas de citas"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    doctor_id = request.query_params.get('doctor_id')
    specialty = request.query_params.get('specialty')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    data = AnalyticsService.get_appointment_stats(
        start_date=start_date,
        end_date=end_date,
        doctor_id=doctor_id,
        specialty=specialty
    )
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def revenue_analysis_api(request):
    """API para análisis de ingresos"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    by_doctor = request.query_params.get('by_doctor', 'false').lower() == 'true'
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    data = AnalyticsService.get_revenue_analysis(
        start_date=start_date,
        end_date=end_date,
        by_doctor=by_doctor
    )
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_performance_api(request):
    """API para métricas de rendimiento de médicos"""
    doctor_id = request.query_params.get('doctor_id')
    period = int(request.query_params.get('period', 30))
    
    data = AnalyticsService.get_doctor_performance(
        doctor_id=doctor_id,
        period=period
    )
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def specialty_demand_api(request):
    """API para análisis de demanda por especialidad"""
    data = AnalyticsService.get_specialty_demand()
    return Response(data)

# Vistas regulares de Django para renderizar páginas
@login_required
def dashboard(request):
    """Dashboard principal de informes"""
    return render(request, 'reports/dashboard.html')

@login_required
def appointment_report(request):
    """Página de informe de citas"""
    return render(request, 'reports/appointment_report.html')

@login_required
def revenue_report(request):
    """Página de informe de ingresos"""
    return render(request, 'reports/revenue_report.html')

@staff_member_required
def doctor_performance_report(request):
    """Página de informe de rendimiento de médicos (solo staff)"""
    return render(request, 'reports/doctor_performance.html')

@staff_member_required
def specialty_analysis(request):
    """Página de análisis de especialidades (solo staff)"""
    return render(request, 'reports/specialty_analysis.html')

# ViewSets para gestión de informes guardados
class ReportViewSet(viewsets.ModelViewSet):
    """API para gestionar informes guardados"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SavedDashboardViewSet(viewsets.ModelViewSet):
    """API para gestionar dashboards guardados"""
    serializer_class = SavedDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedDashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
