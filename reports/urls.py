from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'saved-reports', views.ReportViewSet, basename='report')
router.register(r'saved-dashboards', views.SavedDashboardViewSet, basename='dashboard')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/appointments/', views.appointment_stats_api, name='api-appointments-stats'),
    path('api/stats/revenue/', views.revenue_analysis_api, name='api-revenue-stats'),
    path('api/stats/doctor-performance/', views.doctor_performance_api, name='api-doctor-performance'),
    path('api/stats/specialty-demand/', views.specialty_demand_api, name='api-specialty-demand'),
    
    # Páginas web
    path('', views.dashboard, name='reports-dashboard'),
    path('appointments/', views.appointment_report, name='appointment-report'),
    path('revenue/', views.revenue_report, name='revenue-report'),
    path('doctor-performance/', views.doctor_performance_report, name='doctor-performance-report'),
    path('specialty-analysis/', views.specialty_analysis, name='specialty-analysis'),
] 
