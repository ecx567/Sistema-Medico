from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
#from doctors.models import Doctor

from accounts.models import User

class AnalyticsService:
    """Servicio para generar análisis de datos del sistema"""
    
    @staticmethod
    def get_appointment_stats(start_date=None, end_date=None, doctor_id=None, specialty=None):
        """Obtiene estadísticas de citas según filtros"""
        queryset = Booking.objects.all()
        
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if specialty:
            queryset = queryset.filter(doctor__speciality=specialty)
            
        # Estadísticas generales
        total_appointments = queryset.count()
        completed = queryset.filter(status='completed').count()
        cancelled = queryset.filter(status='cancelled').count()
        
        # Tendencia por tiempo
        by_month = (
            queryset
            .annotate(month=TruncMonth('appointment_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        # Estado por especialidad
        by_specialty = (
            queryset
            .values('doctor__speciality')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        return {
            'total': total_appointments,
            'completed': completed,
            'cancelled': cancelled,
            'completion_rate': (completed / total_appointments * 100) if total_appointments else 0,
            'by_month': list(by_month),
            'by_specialty': list(by_specialty),
        }
    
    @staticmethod
    def get_revenue_analysis(start_date=None, end_date=None, by_doctor=False):
        """Análisis de ingresos"""
        queryset = Booking.objects.filter(status='completed')
        
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        
        # Ingresos totales
        total_revenue = queryset.aggregate(total=Sum('fee'))['total'] or 0
        
        # Tendencia por mes
        revenue_by_month = (
            queryset
            .annotate(month=TruncMonth('appointment_date'))
            .values('month')
            .annotate(revenue=Sum('fee'))
            .order_by('month')
        )
        
        # Ingresos por médico si se solicita
        revenue_by_doctor = []
        if by_doctor:
            revenue_by_doctor = (
                queryset
                .values('doctor__user__first_name', 'doctor__user__last_name', 'doctor_id')
                .annotate(
                    revenue=Sum('fee'),
                    appointments=Count('id'),
                    avg_fee=Avg('fee')
                )
                .order_by('-revenue')
            )
        
        return {
            'total_revenue': total_revenue,
            'by_month': list(revenue_by_month),
            'by_doctor': list(revenue_by_doctor),
        }
    
    @staticmethod
    def get_doctor_performance(doctor_id=None, period=30):
        """Métricas de rendimiento de médicos"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period)
        
        queryset = Booking.objects.filter(
            appointment_date__range=(start_date, end_date)
        )
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Análisis por médico
        performance = (
            queryset
            .values('doctor__user__first_name', 'doctor__user__last_name', 'doctor_id')
            .annotate(
                total_appointments=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                cancelled=Count('id', filter=Q(status='cancelled')),
                revenue=Sum('fee', filter=Q(status='completed')),
                avg_rating=Avg('doctor__reviews__rating')
            )
            .order_by('-total_appointments')
        )
        
        return list(performance)
    
    @staticmethod
    def get_specialty_demand():
        """Análisis de demanda por especialidad"""
        # Citas por especialidad
        bookings_by_specialty = (
            Booking.objects.values('doctor__speciality')
            .annotate(
                count=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                revenue=Sum('fee', filter=Q(status='completed'))
            )
            .order_by('-count')
        )
        
        # Médicos por especialidad
        doctors_by_specialty = (
            Doctor.objects.values('speciality')
            .annotate(count=Count('id'))
            .order_by('speciality')
        )
        
        return {
            'bookings': list(bookings_by_specialty),
            'doctors': list(doctors_by_specialty)
        }
