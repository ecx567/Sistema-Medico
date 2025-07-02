from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('settings/', views.reminder_settings, name='settings'),
    path('history/', views.reminder_history, name='history'),
    path('send-test/<int:booking_id>/', views.send_test_reminder, name='send-test'),
    path('preferences/', views.user_reminder_preferences, name='preferences'),
]
