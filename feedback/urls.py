from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Para pacientes
    path('leave/<int:booking_id>/', views.leave_feedback, name='leave'),
    
    # Para médicos
    path('my-feedbacks/', views.doctor_feedbacks, name='doctor-feedbacks'),
    path('respond/<int:feedback_id>/', views.respond_to_feedback, name='respond'),
    
    # Para administradores
    path('admin/', views.admin_feedbacks, name='admin-feedbacks'),
    path('admin/approve/<int:feedback_id>/', views.approve_feedback, name='approve'),
    path('admin/reject/<int:feedback_id>/', views.reject_feedback, name='reject'),
]
