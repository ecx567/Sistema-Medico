from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('dashboard/', views.audit_dashboard, name='dashboard'),
    path('logs/', views.audit_logs, name='logs'),
    path('settings/', views.audit_settings, name='settings'),
]
