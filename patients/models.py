from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
# Create your models here.


class MedicalRecord(models.Model):
    """Modelo para almacenar el historial médico detallado de los pacientes"""
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name=_("Paciente")
    )
    
    # Información médica detallada
    allergies = models.TextField(_("Alergias"), blank=True, help_text=_("Liste todas las alergias conocidas"))
    medications = models.TextField(_("Medicamentos actuales"), blank=True, help_text=_("Liste los medicamentos que está tomando actualmente"))
    chronic_diseases = models.TextField(_("Enfermedades crónicas"), blank=True, help_text=_("Liste las enfermedades crónicas diagnosticadas"))
    previous_surgeries = models.TextField(_("Cirugías previas"), blank=True, help_text=_("Liste las cirugías previas con fechas aproximadas"))
    family_history = models.TextField(_("Antecedentes familiares"), blank=True, help_text=_("Historial médico familiar relevante"))
    
    # Signos vitales
    blood_type = models.CharField(_("Grupo sanguíneo"), max_length=10, blank=True)
    height = models.DecimalField(_("Altura (cm)"), max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(_("Peso (kg)"), max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Notas adicionales
    notes = models.TextField(_("Notas adicionales"), blank=True)
    
    # Metadatos
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medical_records',
        verbose_name=_("Creado por")
    )
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("Historial médico")
        verbose_name_plural = _("Historiales médicos")
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Historial médico de {self.patient.get_full_name()}"
    
    def get_bmi(self):
        """Calcula el índice de masa corporal"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100  # convertir cm a m
            return round(self.weight / (height_m * height_m), 2)
        return None


class MedicalDiagnosis(models.Model):
    """Modelo para almacenar diagnósticos médicos"""
    
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='diagnoses',
        verbose_name=_("Historial médico")
    )
    
    diagnosis = models.CharField(_("Diagnóstico"), max_length=255)
    diagnosis_date = models.DateField(_("Fecha de diagnóstico"))
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doctor_diagnoses',
        verbose_name=_("Médico")
    )
    treatment = models.TextField(_("Tratamiento"), blank=True)
    notes = models.TextField(_("Notas"), blank=True)
    
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("Diagnóstico médico")
        verbose_name_plural = _("Diagnósticos médicos")
        ordering = ['-diagnosis_date']
    
    def __str__(self):
        return f"{self.diagnosis} - {self.diagnosis_date}"
