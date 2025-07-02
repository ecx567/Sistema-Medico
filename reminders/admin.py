from django.contrib import admin
from .models import ReminderConfiguration, ReminderLog, UserReminderPreference

@admin.register(ReminderConfiguration)
class ReminderConfigurationAdmin(admin.ModelAdmin):
    list_display = ('hours_before', 'enabled', 'updated_at', 'updated_by')
    list_filter = ('enabled',)
    search_fields = ('email_subject',)
    
@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ('booking', 'sent_at', 'sent_to_patient', 'sent_to_doctor')
    list_filter = ('sent_at', 'sent_to_patient', 'sent_to_doctor')
    search_fields = ('booking__patient__username', 'booking__doctor__username')
    date_hierarchy = 'sent_at'

@admin.register(UserReminderPreference)
class UserReminderPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'enabled', 'email_enabled', 'hours_before')
    list_filter = ('enabled', 'email_enabled')
    search_fields = ('user__username', 'user__email')
