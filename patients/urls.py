from django.urls import path

from .views import (
    PatientDashboardView,
    PatientProfileUpdateView,
    AppointmentDetailView,
    AppointmentCancelView,
    AppointmentPrintView,
    ChangePasswordView,
    AddReviewView,
    PatientListView,
    PatientDetailView, 
    PatientEditView,
    after_register_patient,
    doctor_booking,
    get_available_slots_api,
    AppointmentSuccessView ,
    get_available_slots_for_date,
    BookingView,

)
# Importar el módulo medical_records correctamente
#from .views import medical_records
from bookings.views import BookingCreateView, BookingListView

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
    #
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    
    path(
        "appointment/create/<int:doctor_id>/",
        BookingCreateView.as_view(),
        name="book-appointment",
    ),
    path(
        "appointments/",
        BookingListView.as_view(),
        name="patient-appointments",
    ),
    path(
        "add-review/<int:doctor_id>/",
        AddReviewView.as_view(),
        name="add-review",
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
    # Nueva URL para listar pacientes
    path(
        "list/",
        PatientListView.as_view(),
        name="patients-list",
    ),
    path(
    "patient/<int:pk>/",
    PatientDetailView.as_view(),
    name="patient-detail",
    ),
    path(
        "patient/<int:pk>/edit/",
        PatientEditView.as_view(),
        name="patient-edit",
    ),
    #
    path(
        "after-register/<int:pk>/",
        after_register_patient,
        name="after-register",
    ),
    path(
        "doctor-booking/<int:doctor_pk>/<int:patient_pk>/",
        doctor_booking,
        name="doctor-booking",
    ),
    path(
    "appointments/<int:booking_id>/success/",
    AppointmentSuccessView.as_view(),
    name="appointment-success",
    ),
    # API endpoints
    path('api/doctor/<int:doctor_pk>/slots/', get_available_slots_api, name='get-available-slots'),

    # URL para la página de reserva
    path('doctor-booking/<int:speciality_id>/<int:doctor_id>/', BookingView.as_view(), name='doctor-booking'),

    # URL para la petición AJAX de los horarios
    path('get-available-slots/<int:doctor_id>/<str:date_str>/', get_available_slots_for_date, name='get-available-slots'),

    # URLs para historial médico
    #path('medical-record/', medical_records.my_medical_record, name='my_medical_record'),
    #path('medical-record/edit/', medical_records.edit_my_medical_record, name='edit_my_medical_record'),
    #path('patient/<int:patient_id>/medical-record/', medical_records.medical_record_detail, name='medical_record_detail'),
    #path('patient/<int:patient_id>/medical-record/edit/', medical_records.medical_record_edit, name='medical_record_edit'),
    #path('patient/<int:patient_id>/diagnosis/add/', medical_records.diagnosis_create, name='diagnosis_create'),
    #path('diagnosis/<int:diagnosis_id>/edit/', medical_records.diagnosis_edit, name='diagnosis_edit'),
]
