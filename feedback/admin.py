from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('patient__username', 'doctor__username', 'comment')
    readonly_fields = ('patient', 'doctor', 'booking', 'rating', 'comment', 'created_at')
    actions = ['approve_feedback', 'reject_feedback']
    
    def approve_feedback(self, request, queryset):
        queryset.update(is_approved=True)
    approve_feedback.short_description = "Aprobar retroalimentaciones seleccionadas"
    
    def reject_feedback(self, request, queryset):
        queryset.update(is_approved=False)
    reject_feedback.short_description = "Rechazar retroalimentaciones seleccionadas"
