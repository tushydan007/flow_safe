"""
Serializers for analysis-related models.
"""

from rest_framework import serializers

from .models import (
    AnalysisResult, LeakDetection, ChangeDetection,
    EncroachmentDetection, EmissionDetection, FacilityMonitoring
)


class LeakDetectionSerializer(serializers.ModelSerializer):
    """Serializer for LeakDetection model."""
    
    class Meta:
        model = LeakDetection
        fields = (
            'id',
            'location',
            'location_name',
            'ndvi_value',
            'confidence',
            'extent_sqm',
            'severity',
            'description',
            'detected_at',
        )


class ChangeDetectionSerializer(serializers.ModelSerializer):
    """Serializer for ChangeDetection model."""
    
    change_type_display = serializers.CharField(
        source='get_change_type_display',
        read_only=True
    )
    
    class Meta:
        model = ChangeDetection
        fields = (
            'id',
            'location',
            'location_name',
            'change_type',
            'change_type_display',
            'change_percentage',
            'confidence',
            'area_sqm',
            'severity',
            'description',
            'detected_at',
        )


class EncroachmentDetectionSerializer(serializers.ModelSerializer):
    """Serializer for EncroachmentDetection model."""
    
    object_type_display = serializers.CharField(
        source='get_object_type_display',
        read_only=True
    )
    
    class Meta:
        model = EncroachmentDetection
        fields = (
            'id',
            'location',
            'location_name',
            'object_type',
            'object_type_display',
            'object_label',
            'confidence',
            'bounding_box',
            'distance_to_pipeline_m',
            'severity',
            'description',
            'detected_at',
        )


class EmissionDetectionSerializer(serializers.ModelSerializer):
    """Serializer for EmissionDetection model."""
    
    emission_type_display = serializers.CharField(
        source='get_emission_type_display',
        read_only=True
    )
    
    class Meta:
        model = EmissionDetection
        fields = (
            'id',
            'location',
            'location_name',
            'emission_type',
            'emission_type_display',
            'intensity',
            'confidence',
            'estimated_volume',
            'severity',
            'description',
            'detected_at',
        )


class FacilityMonitoringSerializer(serializers.ModelSerializer):
    """Serializer for FacilityMonitoring model."""
    
    facility_type_display = serializers.CharField(
        source='get_facility_type_display',
        read_only=True
    )
    condition_display = serializers.CharField(
        source='get_condition_display',
        read_only=True
    )
    
    class Meta:
        model = FacilityMonitoring
        fields = (
            'id',
            'location',
            'location_name',
            'facility_type',
            'facility_type_display',
            'condition',
            'condition_display',
            'confidence',
            'segmentation_mask',
            'area_sqm',
            'severity',
            'description',
            'detected_at',
        )


class AnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisResult model."""
    
    analysis_type_display = serializers.CharField(
        source='get_analysis_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    satellite_image_name = serializers.CharField(
        source='satellite_image.name',
        read_only=True
    )
    detections_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisResult
        fields = (
            'id',
            'satellite_image',
            'satellite_image_name',
            'analysis_type',
            'analysis_type_display',
            'status',
            'status_display',
            'progress',
            'error_message',
            'chunks_total',
            'chunks_processed',
            'processing_time_seconds',
            'summary',
            'severity',
            'result_data',
            'result_geojson',
            'result_image',
            'started_at',
            'completed_at',
            'detections_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'analysis_type_display',
            'status_display',
            'satellite_image_name',
            'detections_count',
            'created_at',
            'updated_at',
        )
    
    def get_detections_count(self, obj):
        """Get count of detections for this analysis."""
        result_data = obj.result_data or {}
        return result_data.get('total_anomalies', 
                               result_data.get('total_changes',
                               result_data.get('total_objects',
                               result_data.get('total_facilities', 0))))


class AnalysisResultDetailSerializer(AnalysisResultSerializer):
    """Detailed serializer for AnalysisResult with all detections."""
    
    leak_detections = LeakDetectionSerializer(many=True, read_only=True)
    change_detections = ChangeDetectionSerializer(many=True, read_only=True)
    encroachment_detections = EncroachmentDetectionSerializer(many=True, read_only=True)
    emission_detections = EmissionDetectionSerializer(many=True, read_only=True)
    facility_monitoring = FacilityMonitoringSerializer(many=True, read_only=True)
    
    class Meta(AnalysisResultSerializer.Meta):
        fields = AnalysisResultSerializer.Meta.fields + (
            'leak_detections',
            'change_detections',
            'encroachment_detections',
            'emission_detections',
            'facility_monitoring',
        )


class AnalysisResultListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing analysis results."""
    
    analysis_type_display = serializers.CharField(
        source='get_analysis_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = AnalysisResult
        fields = (
            'id',
            'analysis_type',
            'analysis_type_display',
            'status',
            'status_display',
            'progress',
            'severity',
            'summary',
            'completed_at',
            'created_at',
        )


class RunAnalysisSerializer(serializers.Serializer):
    """Serializer for running analysis."""
    
    analysis_types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['ndvi', 'change', 'encroachment', 'emission', 'facility', 'all']
        ),
        required=False,
        default=['all']
    )


class ImageAnalysisSummarySerializer(serializers.Serializer):
    """Serializer for image analysis summary."""
    
    image_id = serializers.IntegerField()
    image_name = serializers.CharField()
    acquisition_date = serializers.DateField()
    is_analyzed = serializers.BooleanField()
    analysis_results = AnalysisResultListSerializer(many=True)
    total_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    overall_status = serializers.CharField()

