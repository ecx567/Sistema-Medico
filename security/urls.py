from django.urls import path, include

urlpatterns = [
    path('permissions/', include('security.permissions.urls')),
    path('audit/', include('security.audit.urls')),

]
