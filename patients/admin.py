from django.contrib import admin
from .models import MedicalRecord, MedicalDiagnosis

# Register your models here.
#
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'updated_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__email')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('patient', 'created_by')
        }),
        ('Información Médica', {
            'fields': ('allergies', 'medications', 'chronic_diseases', 'previous_surgeries', 'family_history')
        }),
        ('Signos Vitales', {
            'fields': ('blood_type', 'height', 'weight')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(MedicalDiagnosis)
class MedicalDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('diagnosis', 'medical_record', 'diagnosis_date', 'doctor')
    search_fields = ('diagnosis', 'medical_record__patient__first_name', 'medical_record__patient__last_name')
    list_filter = ('diagnosis_date', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
