"""
Serializers for pipeline-related models.
"""

from rest_framework import serializers

from .models import PipelineRoute, SatelliteImage, Alert


class PipelineRouteSerializer(serializers.ModelSerializer):
    """
    Serializer for PipelineRoute model.
    """
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )

    class Meta:
        model = PipelineRoute
        fields = (
            'id',
            'name',
            'description',
            'geojson_file',
            'geojson_data',
            'total_length_km',
            'start_point',
            'end_point',
            'bounds',
            'color',
            'is_active',
            'organization_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'geojson_data',
            'total_length_km',
            'start_point',
            'end_point',
            'bounds',
            'organization_name',
            'created_at',
            'updated_at',
        )


class PipelineRouteListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing pipeline routes.
    """
    class Meta:
        model = PipelineRoute
        fields = (
            'id',
            'name',
            'bounds',
            'color',
            'is_active',
            'created_at',
        )


class SatelliteImageSerializer(serializers.ModelSerializer):
    """
    Serializer for SatelliteImage model.
    """
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )
    pipeline_name = serializers.CharField(
        source='pipeline.name',
        read_only=True,
        allow_null=True
    )
    display_name = serializers.SerializerMethodField()
    has_alerts = serializers.SerializerMethodField()

    class Meta:
        model = SatelliteImage
        fields = (
            'id',
            'name',
            'display_name',
            'description',
            'original_file',
            'cog_file',
            'acquisition_date',
            'satellite_name',
            'resolution',
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
            'pipeline',
            'pipeline_name',
            'organization_name',
            'has_alerts',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'display_name',
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
            'organization_name',
            'pipeline_name',
            'has_alerts',
            'created_at',
            'updated_at',
        )

    def get_display_name(self, obj):
        """Generate display name with acquisition date."""
        date_str = obj.acquisition_date.strftime('%Y-%m-%d') if obj.acquisition_date else 'Unknown date'
        return f"{obj.name} ({date_str})"

    def get_has_alerts(self, obj):
        """Check if image has unacknowledged alerts."""
        return obj.alerts.filter(is_acknowledged=False).exists()


class SatelliteImageListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing satellite images.
    """
    display_name = serializers.SerializerMethodField()
    has_unacknowledged_alerts = serializers.SerializerMethodField()

    class Meta:
        model = SatelliteImage
        fields = (
            'id',
            'name',
            'display_name',
            'acquisition_date',
            'status',
            'is_analyzed',
            'has_unacknowledged_alerts',
            'created_at',
        )

    def get_display_name(self, obj):
        """Generate display name with acquisition date."""
        date_str = obj.acquisition_date.strftime('%Y-%m-%d') if obj.acquisition_date else 'Unknown date'
        return f"{obj.name} ({date_str})"

    def get_has_unacknowledged_alerts(self, obj):
        """Check if image has unacknowledged alerts."""
        return obj.alerts.filter(is_acknowledged=False).exists()


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model.
    """
    alert_type_display = serializers.CharField(
        source='get_alert_type_display',
        read_only=True
    )
    severity_display = serializers.CharField(
        source='get_severity_display',
        read_only=True
    )
    satellite_image_name = serializers.CharField(
        source='satellite_image.name',
        read_only=True,
        allow_null=True
    )
    pipeline_name = serializers.CharField(
        source='pipeline.name',
        read_only=True,
        allow_null=True
    )
    acknowledged_by_email = serializers.CharField(
        source='acknowledged_by.email',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Alert
        fields = (
            'id',
            'alert_type',
            'alert_type_display',
            'severity',
            'severity_display',
            'title',
            'description',
            'location',
            'location_name',
            'is_acknowledged',
            'acknowledged_at',
            'acknowledged_by',
            'acknowledged_by_email',
            'satellite_image',
            'satellite_image_name',
            'pipeline',
            'pipeline_name',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'alert_type_display',
            'severity_display',
            'satellite_image_name',
            'pipeline_name',
            'acknowledged_by_email',
            'created_at',
            'updated_at',
        )


class AlertAcknowledgeSerializer(serializers.Serializer):
    """
    Serializer for acknowledging alerts.
    """
    alert_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )

