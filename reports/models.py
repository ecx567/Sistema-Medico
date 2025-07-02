from django.db import models
from django.conf import settings

class Report(models.Model):
    """Modelo para guardar informes generados"""
    REPORT_TYPES = (
        ('appointment', 'Informe de Citas'),
        ('revenue', 'Informe de Ingresos'),
        ('doctor_performance', 'Rendimiento de Médicos'),
        ('patient_stats', 'Estadísticas de Pacientes'),
        ('specialty_demand', 'Demanda por Especialidad'),
    )
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict, help_text="Parámetros utilizados para generar el informe")
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Informe'
        verbose_name_plural = 'Informes'


class SavedDashboard(models.Model):
    """Modelo para guardar configuraciones personalizadas de dashboard"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        unique_together = ['user', 'name']
