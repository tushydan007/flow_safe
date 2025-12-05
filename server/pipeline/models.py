"""
Models for pipeline routes and satellite imagery.
"""

import os
import json
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from user.models import Organization


def pipeline_geojson_path(instance, filename):
    """Generate path for pipeline GeoJSON files."""
    return f'pipelines/{instance.organization.user.id}/{filename}'


def satellite_image_path(instance, filename):
    """Generate path for satellite images."""
    return f'satellite_images/{instance.organization.user.id}/{filename}'


def cog_image_path(instance, filename):
    """Generate path for Cloud Optimized GeoTIFF files."""
    return f'cog_images/{instance.organization.user.id}/{filename}'


class PipelineRoute(models.Model):
    """
    Model for pipeline route GeoJSON data.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='pipeline_routes'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    geojson_file = models.FileField(
        _('GeoJSON file'),
        upload_to=pipeline_geojson_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['geojson', 'json']
            )
        ]
    )
    geojson_data = models.JSONField(
        _('GeoJSON data'),
        blank=True,
        null=True
    )
    total_length_km = models.FloatField(
        _('total length (km)'),
        blank=True,
        null=True
    )
    start_point = models.JSONField(
        _('start point'),
        blank=True,
        null=True
    )
    end_point = models.JSONField(
        _('end point'),
        blank=True,
        null=True
    )
    bounds = models.JSONField(
        _('bounds'),
        blank=True,
        null=True,
        help_text='Bounding box [minLng, minLat, maxLng, maxLat]'
    )
    color = models.CharField(
        _('display color'),
        max_length=7,
        default='#FF5722'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('pipeline route')
        verbose_name_plural = _('pipeline routes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

    def save(self, *args, **kwargs):
        """Parse GeoJSON file and extract metadata on save."""
        super().save(*args, **kwargs)
        
        if self.geojson_file and not self.geojson_data:
            try:
                self.geojson_file.seek(0)
                content = self.geojson_file.read().decode('utf-8')
                self.geojson_data = json.loads(content)
                self._extract_metadata()
                super().save(update_fields=['geojson_data', 'bounds', 'start_point', 'end_point'])
            except (json.JSONDecodeError, IOError):
                pass

    def _extract_metadata(self):
        """Extract metadata from GeoJSON data."""
        if not self.geojson_data:
            return

        features = self.geojson_data.get('features', [])
        if not features:
            return

        all_coords = []
        for feature in features:
            geometry = feature.get('geometry', {})
            geom_type = geometry.get('type', '')
            coords = geometry.get('coordinates', [])

            if geom_type == 'LineString':
                all_coords.extend(coords)
            elif geom_type == 'MultiLineString':
                for line in coords:
                    all_coords.extend(line)
            elif geom_type == 'Point':
                all_coords.append(coords)

        if all_coords:
            lngs = [c[0] for c in all_coords if len(c) >= 2]
            lats = [c[1] for c in all_coords if len(c) >= 2]
            
            if lngs and lats:
                self.bounds = [min(lngs), min(lats), max(lngs), max(lats)]
                self.start_point = {'lng': all_coords[0][0], 'lat': all_coords[0][1]}
                self.end_point = {'lng': all_coords[-1][0], 'lat': all_coords[-1][1]}


class SatelliteImage(models.Model):
    """
    Model for satellite imagery (TIFF files).
    """
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='satellite_images'
    )
    pipeline = models.ForeignKey(
        PipelineRoute,
        on_delete=models.CASCADE,
        related_name='satellite_images',
        blank=True,
        null=True
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    original_file = models.FileField(
        _('original image'),
        upload_to=satellite_image_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['tif', 'tiff', 'TIF', 'TIFF']
            )
        ],
        help_text='Upload TIFF/GeoTIFF files only'
    )
    cog_file = models.FileField(
        _('Cloud Optimized GeoTIFF'),
        upload_to=cog_image_path,
        blank=True,
        null=True
    )
    acquisition_date = models.DateField(
        _('acquisition date'),
        blank=True,
        null=True
    )
    satellite_name = models.CharField(
        _('satellite name'),
        max_length=100,
        blank=True
    )
    resolution = models.FloatField(
        _('resolution (m/pixel)'),
        blank=True,
        null=True
    )
    bounds = models.JSONField(
        _('bounds'),
        blank=True,
        null=True,
        help_text='Bounding box [minLng, minLat, maxLng, maxLat]'
    )
    center = models.JSONField(
        _('center'),
        blank=True,
        null=True,
        help_text='Center point {lng, lat}'
    )
    width = models.IntegerField(_('width (pixels)'), blank=True, null=True)
    height = models.IntegerField(_('height (pixels)'), blank=True, null=True)
    bands = models.IntegerField(_('number of bands'), blank=True, null=True)
    file_size = models.BigIntegerField(_('file size (bytes)'), blank=True, null=True)
    crs = models.CharField(_('coordinate reference system'), max_length=100, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploading'
    )
    error_message = models.TextField(_('error message'), blank=True)
    is_analyzed = models.BooleanField(_('is analyzed'), default=False)
    analysis_completed_at = models.DateTimeField(
        _('analysis completed at'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('satellite image')
        verbose_name_plural = _('satellite images')
        ordering = ['-acquisition_date', '-created_at']

    def __str__(self):
        date_str = self.acquisition_date.strftime('%Y-%m-%d') if self.acquisition_date else 'Unknown date'
        return f"{self.name} - {date_str}"

    def save(self, *args, **kwargs):
        """Extract metadata from TIFF file on save."""
        if self.original_file:
            self.file_size = self.original_file.size
        super().save(*args, **kwargs)


class Alert(models.Model):
    """
    Model for system alerts and notifications.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    ALERT_TYPE_CHOICES = [
        ('leak', 'Leak Detected'),
        ('change', 'Change Detected'),
        ('encroachment', 'Encroachment Detected'),
        ('emission', 'Emission Detected'),
        ('facility', 'Facility Issue'),
        ('system', 'System Alert'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    satellite_image = models.ForeignKey(
        SatelliteImage,
        on_delete=models.CASCADE,
        related_name='alerts',
        blank=True,
        null=True
    )
    pipeline = models.ForeignKey(
        PipelineRoute,
        on_delete=models.CASCADE,
        related_name='alerts',
        blank=True,
        null=True
    )
    alert_type = models.CharField(
        _('alert type'),
        max_length=20,
        choices=ALERT_TYPE_CHOICES
    )
    severity = models.CharField(
        _('severity'),
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    location = models.JSONField(
        _('location'),
        blank=True,
        null=True,
        help_text='Location coordinates {lng, lat}'
    )
    location_name = models.CharField(
        _('location name'),
        max_length=255,
        blank=True
    )
    is_acknowledged = models.BooleanField(_('is acknowledged'), default=False)
    acknowledged_at = models.DateTimeField(
        _('acknowledged at'),
        blank=True,
        null=True
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='acknowledged_alerts'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('alert')
        verbose_name_plural = _('alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title}"

