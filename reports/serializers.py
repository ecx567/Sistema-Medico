from rest_framework import serializers
from .models import Report, SavedDashboard

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title', 'report_type', 'created_by', 'created_at', 'parameters', 'is_public']
        read_only_fields = ['created_by', 'created_at']

class SavedDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedDashboard
        fields = ['id', 'user', 'name', 'configuration', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
