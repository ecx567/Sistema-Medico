from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    path('manage/', views.manage_permissions, name='manage'),
]
