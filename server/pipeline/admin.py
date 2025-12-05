"""
Admin configuration for pipeline app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import PipelineRoute, SatelliteImage, Alert
from analysis.tasks import process_satellite_image, run_all_analyses


@admin.register(PipelineRoute)
class PipelineRouteAdmin(admin.ModelAdmin):
    """Admin for PipelineRoute model."""
    
    list_display = (
        'name',
        'organization',
        'total_length_km',
        'color_preview',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'created_at', 'organization')
    search_fields = ('name', 'description', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = (
        'geojson_data',
        'bounds',
        'start_point',
        'end_point',
        'total_length_km',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'geojson_file')
        }),
        (_('Display Options'), {
            'fields': ('color', 'is_active')
        }),
        (_('Extracted Data'), {
            'fields': ('geojson_data', 'bounds', 'start_point', 'end_point', 'total_length_km'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def color_preview(self, obj):
        """Display color preview."""
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; border-radius: 3px;">&nbsp;</span>',
            obj.color
        )
    color_preview.short_description = 'Color'


@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    """Admin for SatelliteImage model."""
    
    list_display = (
        'name',
        'organization',
        'acquisition_date',
        'status_badge',
        'is_analyzed',
        'file_size_display',
        'created_at',
    )
    list_filter = ('status', 'is_analyzed', 'acquisition_date', 'organization')
    search_fields = ('name', 'description', 'organization__name', 'satellite_name')
    ordering = ('-acquisition_date', '-created_at')
    readonly_fields = (
        'cog_file',
        'bounds',
        'center',
        'width',
        'height',
        'bands',
        'file_size',
        'crs',
        'status',
        'error_message',
        'is_analyzed',
        'analysis_completed_at',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'pipeline', 'name', 'description')
        }),
        (_('Image File'), {
            'fields': ('original_file', 'cog_file')
        }),
        (_('Metadata'), {
            'fields': ('acquisition_date', 'satellite_name', 'resolution')
        }),
        (_('Extracted Data'), {
            'fields': ('bounds', 'center', 'width', 'height', 'bands', 'file_size', 'crs'),
            'classes': ('collapse',)
        }),
        (_('Processing Status'), {
            'fields': ('status', 'error_message', 'is_analyzed', 'analysis_completed_at'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['process_images', 'run_analysis', 'convert_to_cog']

    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'uploading': '#FFA500',
            'processing': '#2196F3',
            'ready': '#4CAF50',
            'error': '#F44336',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#9E9E9E'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def file_size_display(self, obj):
        """Display file size in human readable format."""
        if not obj.file_size:
            return '-'
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    file_size_display.short_description = 'File Size'

    @admin.action(description='Process selected images (extract metadata & convert to COG)')
    def process_images(self, request, queryset):
        """Process selected satellite images."""
        for image in queryset:
            process_satellite_image.delay(image.id)
        self.message_user(
            request,
            f"Processing started for {queryset.count()} image(s). Check back for results."
        )

    @admin.action(description='Run all analyses on selected images')
    def run_analysis(self, request, queryset):
        """Run all analyses on selected images."""
        for image in queryset.filter(status='ready'):
            run_all_analyses.delay(image.id)
        self.message_user(
            request,
            f"Analysis started for {queryset.filter(status='ready').count()} ready image(s)."
        )

    @admin.action(description='Convert selected images to Cloud Optimized GeoTIFF')
    def convert_to_cog(self, request, queryset):
        """Convert selected images to COG format."""
        from analysis.tasks import convert_to_cog
        for image in queryset:
            convert_to_cog.delay(image.id)
        self.message_user(
            request,
            f"COG conversion started for {queryset.count()} image(s)."
        )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin for Alert model."""
    
    list_display = (
        'title',
        'alert_type',
        'severity_badge',
        'organization',
        'is_acknowledged',
        'created_at',
    )
    list_filter = (
        'alert_type',
        'severity',
        'is_acknowledged',
        'created_at',
        'organization'
    )
    search_fields = ('title', 'description', 'location_name', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'satellite_image', 'pipeline')
        }),
        (_('Alert Details'), {
            'fields': ('alert_type', 'severity', 'title', 'description')
        }),
        (_('Location'), {
            'fields': ('location', 'location_name')
        }),
        (_('Acknowledgement'), {
            'fields': ('is_acknowledged', 'acknowledged_at', 'acknowledged_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['acknowledge_alerts', 'mark_as_critical']

    def severity_badge(self, obj):
        """Display severity with color badge."""
        colors = {
            'low': '#8BC34A',
            'medium': '#FFC107',
            'high': '#FF9800',
            'critical': '#F44336',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.severity, '#9E9E9E'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    @admin.action(description='Acknowledge selected alerts')
    def acknowledge_alerts(self, request, queryset):
        """Acknowledge selected alerts."""
        from django.utils import timezone
        count = queryset.filter(is_acknowledged=False).update(
            is_acknowledged=True,
            acknowledged_at=timezone.now(),
            acknowledged_by=request.user
        )
        self.message_user(request, f"{count} alert(s) acknowledged.")

    @admin.action(description='Mark selected alerts as critical')
    def mark_as_critical(self, request, queryset):
        """Mark selected alerts as critical severity."""
        count = queryset.update(severity='critical')
        self.message_user(request, f"{count} alert(s) marked as critical.")

