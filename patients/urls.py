from django.urls import path

from .views import (
    PatientDashboardView,
    PatientProfileUpdateView,
    AppointmentDetailView,
    AppointmentCancelView,
    AppointmentPrintView,
    ChangePasswordView,
    AddReviewView,
)
# Importar el módulo medical_records correctamente
#from .views import medical_records

app_name = "patients"

urlpatterns = [
    path("dashboard/", PatientDashboardView.as_view(), name="dashboard"),
    path(
        "profile-settings/",
        PatientProfileUpdateView.as_view(),
        name="profile-setting",
    ),
    path(
        "appointments/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        AppointmentCancelView.as_view(),
        name="appointment-cancel",
    ),
    #path(
       # "appointment/cancel/<int:pk>/",
      #  AppointmentCancelView.as_view(),
     #   name="appointment-cancel",
    #),
    path(
        "appointments/<int:pk>/print/",
        AppointmentPrintView.as_view(),
        name="appointment-print",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "appointment/<int:booking_id>/review/",
        AddReviewView.as_view(),
        name="add-review",
    ),
    # comentar por si no se quiere
    path(
        "appointment/<int:doctor_id>/review/",
        AddReviewView.as_view(),
        name="add-review",
    ),
    # URLs para historial médico
    #path('medical-record/', medical_records.my_medical_record, name='my_medical_record'),
    #path('medical-record/edit/', medical_records.edit_my_medical_record, name='edit_my_medical_record'),
    #path('patient/<int:patient_id>/medical-record/', medical_records.medical_record_detail, name='medical_record_detail'),
    #path('patient/<int:patient_id>/medical-record/edit/', medical_records.medical_record_edit, name='medical_record_edit'),
    #path('patient/<int:patient_id>/diagnosis/add/', medical_records.diagnosis_create, name='diagnosis_create'),
    #path('diagnosis/<int:diagnosis_id>/edit/', medical_records.diagnosis_edit, name='diagnosis_edit'),
]
