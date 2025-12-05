"""
Models for satellite image analysis results.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from pipeline.models import SatelliteImage


class AnalysisResult(models.Model):
    """
    Base model for analysis results.
    """
    ANALYSIS_TYPES = [
        ('ndvi', 'NDVI Analysis (Leak Detection)'),
        ('change', 'Change Detection'),
        ('encroachment', 'Encroachment Detection'),
        ('emission', 'Emissions Tracking'),
        ('facility', 'Facility Monitoring'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    satellite_image = models.ForeignKey(
        SatelliteImage,
        on_delete=models.CASCADE,
        related_name='analysis_results'
    )
    analysis_type = models.CharField(
        _('analysis type'),
        max_length=20,
        choices=ANALYSIS_TYPES
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    progress = models.IntegerField(_('progress'), default=0)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Processing metadata
    chunks_total = models.IntegerField(_('total chunks'), default=0)
    chunks_processed = models.IntegerField(_('chunks processed'), default=0)
    processing_time_seconds = models.FloatField(
        _('processing time (seconds)'),
        blank=True,
        null=True
    )
    
    # Result summary
    summary = models.TextField(
        _('summary'),
        blank=True,
        help_text='Human-readable summary of analysis results'
    )
    severity = models.CharField(
        _('severity'),
        max_length=10,
        blank=True,
        help_text='Overall severity of findings'
    )
    
    # Result data
    result_data = models.JSONField(
        _('result data'),
        blank=True,
        null=True,
        help_text='Detailed analysis results in JSON format'
    )
    result_geojson = models.JSONField(
        _('result GeoJSON'),
        blank=True,
        null=True,
        help_text='GeoJSON representation of detected features'
    )
    result_image = models.ImageField(
        _('result image'),
        upload_to='analysis_results/',
        blank=True,
        null=True,
        help_text='Visualization of analysis results'
    )
    
    started_at = models.DateTimeField(_('started at'), blank=True, null=True)
    completed_at = models.DateTimeField(_('completed at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('analysis result')
        verbose_name_plural = _('analysis results')
        ordering = ['-created_at']
        unique_together = ['satellite_image', 'analysis_type']

    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.satellite_image.name}"


class LeakDetection(models.Model):
    """
    Model for leak detection results (NDVI analysis).
    """
    analysis_result = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name='leak_detections'
    )
    location = models.JSONField(
        _('location'),
        help_text='Coordinates {lng, lat}'
    )
    location_name = models.CharField(_('location name'), max_length=255, blank=True)
    ndvi_value = models.FloatField(_('NDVI value'))
    confidence = models.FloatField(_('confidence score'))
    extent_sqm = models.FloatField(
        _('extent (sq meters)'),
        blank=True,
        null=True
    )
    severity = models.CharField(_('severity'), max_length=10)
    description = models.TextField(_('description'))
    detected_at = models.DateTimeField(_('detected at'), auto_now_add=True)

    class Meta:
        verbose_name = _('leak detection')
        verbose_name_plural = _('leak detections')
        ordering = ['-detected_at']

    def __str__(self):
        return f"Leak at {self.location_name or 'Unknown location'}"


class ChangeDetection(models.Model):
    """
    Model for change detection results.
    """
    CHANGE_TYPES = [
        ('vegetation_loss', 'Vegetation Loss'),
        ('vegetation_gain', 'Vegetation Gain'),
        ('construction', 'New Construction'),
        ('erosion', 'Erosion'),
        ('water_change', 'Water Level Change'),
        ('unknown', 'Unknown Change'),
    ]

    analysis_result = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name='change_detections'
    )
    location = models.JSONField(
        _('location'),
        help_text='Coordinates {lng, lat}'
    )
    location_name = models.CharField(_('location name'), max_length=255, blank=True)
    change_type = models.CharField(
        _('change type'),
        max_length=20,
        choices=CHANGE_TYPES
    )
    change_percentage = models.FloatField(_('change percentage'))
    confidence = models.FloatField(_('confidence score'))
    area_sqm = models.FloatField(_('area (sq meters)'), blank=True, null=True)
    severity = models.CharField(_('severity'), max_length=10)
    description = models.TextField(_('description'))
    detected_at = models.DateTimeField(_('detected at'), auto_now_add=True)

    class Meta:
        verbose_name = _('change detection')
        verbose_name_plural = _('change detections')
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.get_change_type_display()} at {self.location_name or 'Unknown'}"


class EncroachmentDetection(models.Model):
    """
    Model for encroachment detection results (YOLO object detection).
    """
    OBJECT_TYPES = [
        ('vehicle', 'Vehicle'),
        ('building', 'Building'),
        ('equipment', 'Equipment'),
        ('person', 'Person'),
        ('animal', 'Animal'),
        ('structure', 'Structure'),
        ('other', 'Other'),
    ]

    analysis_result = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name='encroachment_detections'
    )
    location = models.JSONField(
        _('location'),
        help_text='Coordinates {lng, lat}'
    )
    location_name = models.CharField(_('location name'), max_length=255, blank=True)
    object_type = models.CharField(
        _('object type'),
        max_length=20,
        choices=OBJECT_TYPES
    )
    object_label = models.CharField(_('object label'), max_length=100)
    confidence = models.FloatField(_('confidence score'))
    bounding_box = models.JSONField(
        _('bounding box'),
        help_text='Bounding box coordinates'
    )
    distance_to_pipeline_m = models.FloatField(
        _('distance to pipeline (meters)'),
        blank=True,
        null=True
    )
    severity = models.CharField(_('severity'), max_length=10)
    description = models.TextField(_('description'))
    detected_at = models.DateTimeField(_('detected at'), auto_now_add=True)

    class Meta:
        verbose_name = _('encroachment detection')
        verbose_name_plural = _('encroachment detections')
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.object_label} detected at {self.location_name or 'Unknown'}"


class EmissionDetection(models.Model):
    """
    Model for emissions tracking results.
    """
    EMISSION_TYPES = [
        ('methane', 'Methane'),
        ('co2', 'Carbon Dioxide'),
        ('smoke', 'Smoke/Particulates'),
        ('heat', 'Heat Anomaly'),
        ('other', 'Other'),
    ]

    analysis_result = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name='emission_detections'
    )
    location = models.JSONField(
        _('location'),
        help_text='Coordinates {lng, lat}'
    )
    location_name = models.CharField(_('location name'), max_length=255, blank=True)
    emission_type = models.CharField(
        _('emission type'),
        max_length=20,
        choices=EMISSION_TYPES
    )
    intensity = models.FloatField(_('intensity'))
    confidence = models.FloatField(_('confidence score'))
    estimated_volume = models.FloatField(
        _('estimated volume'),
        blank=True,
        null=True,
        help_text='Estimated emission volume in kg/day'
    )
    severity = models.CharField(_('severity'), max_length=10)
    description = models.TextField(_('description'))
    detected_at = models.DateTimeField(_('detected at'), auto_now_add=True)

    class Meta:
        verbose_name = _('emission detection')
        verbose_name_plural = _('emission detections')
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.get_emission_type_display()} at {self.location_name or 'Unknown'}"


class FacilityMonitoring(models.Model):
    """
    Model for facility monitoring results (U-Net segmentation).
    """
    FACILITY_TYPES = [
        ('pipeline_segment', 'Pipeline Segment'),
        ('valve_station', 'Valve Station'),
        ('pump_station', 'Pump Station'),
        ('storage_tank', 'Storage Tank'),
        ('access_road', 'Access Road'),
        ('other', 'Other'),
    ]

    CONDITION_CHOICES = [
        ('normal', 'Normal'),
        ('minor_issue', 'Minor Issue'),
        ('moderate_issue', 'Moderate Issue'),
        ('severe_issue', 'Severe Issue'),
        ('critical', 'Critical'),
    ]

    analysis_result = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name='facility_monitoring'
    )
    location = models.JSONField(
        _('location'),
        help_text='Coordinates {lng, lat}'
    )
    location_name = models.CharField(_('location name'), max_length=255, blank=True)
    facility_type = models.CharField(
        _('facility type'),
        max_length=20,
        choices=FACILITY_TYPES
    )
    condition = models.CharField(
        _('condition'),
        max_length=20,
        choices=CONDITION_CHOICES
    )
    confidence = models.FloatField(_('confidence score'))
    segmentation_mask = models.JSONField(
        _('segmentation mask'),
        blank=True,
        null=True,
        help_text='Segmentation polygon coordinates'
    )
    area_sqm = models.FloatField(_('area (sq meters)'), blank=True, null=True)
    severity = models.CharField(_('severity'), max_length=10)
    description = models.TextField(_('description'))
    detected_at = models.DateTimeField(_('detected at'), auto_now_add=True)

    class Meta:
        verbose_name = _('facility monitoring')
        verbose_name_plural = _('facility monitoring')
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.get_facility_type_display()} - {self.get_condition_display()}"

