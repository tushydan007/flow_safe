"""
Admin configuration for analysis app.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AnalysisResult, LeakDetection, ChangeDetection,
    EncroachmentDetection, EmissionDetection, FacilityMonitoring
)
from .tasks import run_all_analyses, run_analysis


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    """Admin for AnalysisResult model."""
    
    list_display = (
        'satellite_image',
        'analysis_type',
        'status_badge',
        'severity_badge',
        'progress',
        'processing_time_display',
        'completed_at',
    )
    list_filter = ('analysis_type', 'status', 'severity', 'created_at')
    search_fields = ('satellite_image__name', 'summary')
    ordering = ('-created_at',)
    readonly_fields = (
        'status',
        'progress',
        'error_message',
        'chunks_total',
        'chunks_processed',
        'processing_time_seconds',
        'summary',
        'severity',
        'result_data',
        'result_geojson',
        'started_at',
        'completed_at',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        (None, {
            'fields': ('satellite_image', 'analysis_type')
        }),
        ('Status', {
            'fields': ('status', 'progress', 'error_message')
        }),
        ('Processing', {
            'fields': ('chunks_total', 'chunks_processed', 'processing_time_seconds'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('summary', 'severity', 'result_image'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('result_data', 'result_geojson'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['rerun_analysis']

    def status_badge(self, obj):
        colors = {
            'pending': '#9E9E9E',
            'processing': '#2196F3',
            'completed': '#4CAF50',
            'failed': '#F44336',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#9E9E9E'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def severity_badge(self, obj):
        if not obj.severity:
            return '-'
        colors = {
            'low': '#8BC34A',
            'medium': '#FFC107',
            'high': '#FF9800',
            'critical': '#F44336',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.severity, '#9E9E9E'),
            obj.severity.title()
        )
    severity_badge.short_description = 'Severity'

    def processing_time_display(self, obj):
        if not obj.processing_time_seconds:
            return '-'
        if obj.processing_time_seconds < 60:
            return f"{obj.processing_time_seconds:.1f}s"
        minutes = obj.processing_time_seconds / 60
        return f"{minutes:.1f}m"
    processing_time_display.short_description = 'Time'

    @admin.action(description='Re-run selected analyses')
    def rerun_analysis(self, request, queryset):
        count = 0
        for result in queryset:
            run_analysis.delay(result.satellite_image_id, result.analysis_type)
            count += 1
        self.message_user(request, f"Re-running {count} analysis/analyses.")


@admin.register(LeakDetection)
class LeakDetectionAdmin(admin.ModelAdmin):
    """Admin for LeakDetection model."""
    
    list_display = (
        'id',
        'analysis_result',
        'ndvi_value',
        'severity',
        'extent_sqm',
        'detected_at',
    )
    list_filter = ('severity', 'detected_at')
    search_fields = ('location_name', 'description')
    ordering = ('-detected_at',)


@admin.register(ChangeDetection)
class ChangeDetectionAdmin(admin.ModelAdmin):
    """Admin for ChangeDetection model."""
    
    list_display = (
        'id',
        'analysis_result',
        'change_type',
        'change_percentage',
        'severity',
        'detected_at',
    )
    list_filter = ('change_type', 'severity', 'detected_at')
    search_fields = ('location_name', 'description')
    ordering = ('-detected_at',)


@admin.register(EncroachmentDetection)
class EncroachmentDetectionAdmin(admin.ModelAdmin):
    """Admin for EncroachmentDetection model."""
    
    list_display = (
        'id',
        'analysis_result',
        'object_type',
        'object_label',
        'confidence',
        'distance_to_pipeline_m',
        'severity',
        'detected_at',
    )
    list_filter = ('object_type', 'severity', 'detected_at')
    search_fields = ('location_name', 'object_label', 'description')
    ordering = ('-detected_at',)


@admin.register(EmissionDetection)
class EmissionDetectionAdmin(admin.ModelAdmin):
    """Admin for EmissionDetection model."""
    
    list_display = (
        'id',
        'analysis_result',
        'emission_type',
        'intensity',
        'estimated_volume',
        'severity',
        'detected_at',
    )
    list_filter = ('emission_type', 'severity', 'detected_at')
    search_fields = ('location_name', 'description')
    ordering = ('-detected_at',)


@admin.register(FacilityMonitoring)
class FacilityMonitoringAdmin(admin.ModelAdmin):
    """Admin for FacilityMonitoring model."""
    
    list_display = (
        'id',
        'analysis_result',
        'facility_type',
        'condition',
        'confidence',
        'area_sqm',
        'severity',
        'detected_at',
    )
    list_filter = ('facility_type', 'condition', 'severity', 'detected_at')
    search_fields = ('location_name', 'description')
    ordering = ('-detected_at',)

