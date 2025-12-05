"""
Views for pipeline-related operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Q

from .models import PipelineRoute, SatelliteImage, Alert
from .serializers import (
    PipelineRouteSerializer,
    PipelineRouteListSerializer,
    SatelliteImageSerializer,
    SatelliteImageListSerializer,
    AlertSerializer,
    AlertAcknowledgeSerializer,
)


class PipelineRouteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for pipeline route operations.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return PipelineRouteListSerializer
        return PipelineRouteSerializer

    def get_queryset(self):
        """Return pipeline routes for the current user's organization."""
        user = self.request.user
        if hasattr(user, 'organization'):
            return PipelineRoute.objects.filter(
                organization=user.organization,
                is_active=True
            )
        return PipelineRoute.objects.none()

    def list(self, request, *args, **kwargs):
        """List all pipeline routes for the user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """Get a specific pipeline route."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='geojson')
    def get_geojson(self, request, pk=None):
        """Get the GeoJSON data for a pipeline route."""
        instance = self.get_object()
        if instance.geojson_data:
            return Response({
                'success': True,
                'data': instance.geojson_data
            })
        return Response({
            'success': False,
            'message': 'GeoJSON data not available.'
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='all-geojson')
    def get_all_geojson(self, request):
        """Get all GeoJSON data for the user's pipelines."""
        queryset = self.get_queryset()
        features = []
        
        for pipeline in queryset:
            if pipeline.geojson_data:
                geojson = pipeline.geojson_data
                if 'features' in geojson:
                    for feature in geojson['features']:
                        feature['properties'] = feature.get('properties', {})
                        feature['properties']['pipeline_id'] = pipeline.id
                        feature['properties']['pipeline_name'] = pipeline.name
                        feature['properties']['color'] = pipeline.color
                        features.append(feature)
        
        geojson_collection = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        return Response({
            'success': True,
            'data': geojson_collection
        })


class SatelliteImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for satellite image operations.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return SatelliteImageListSerializer
        return SatelliteImageSerializer

    def get_queryset(self):
        """Return satellite images for the current user's organization."""
        user = self.request.user
        if hasattr(user, 'organization'):
            queryset = SatelliteImage.objects.filter(
                organization=user.organization
            )
            
            # Filter by status
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Filter by analyzed
            is_analyzed = self.request.query_params.get('is_analyzed')
            if is_analyzed is not None:
                queryset = queryset.filter(
                    is_analyzed=is_analyzed.lower() == 'true'
                )
            
            # Filter by pipeline
            pipeline_id = self.request.query_params.get('pipeline')
            if pipeline_id:
                queryset = queryset.filter(pipeline_id=pipeline_id)
            
            return queryset
        return SatelliteImage.objects.none()

    def list(self, request, *args, **kwargs):
        """List all satellite images for the user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """Get a specific satellite image."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='bounds')
    def get_bounds(self, request, pk=None):
        """Get the bounds for a satellite image."""
        instance = self.get_object()
        if instance.bounds:
            return Response({
                'success': True,
                'data': {
                    'bounds': instance.bounds,
                    'center': instance.center
                }
            })
        return Response({
            'success': False,
            'message': 'Bounds not available.'
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='dropdown')
    def dropdown_list(self, request):
        """Get a simplified list for dropdown selection."""
        queryset = self.get_queryset().filter(status='ready')
        data = []
        for image in queryset:
            date_str = image.acquisition_date.strftime('%Y-%m-%d') if image.acquisition_date else 'Unknown'
            data.append({
                'id': image.id,
                'name': image.name,
                'display_name': f"{image.name} - {date_str}",
                'acquisition_date': image.acquisition_date,
                'is_analyzed': image.is_analyzed,
            })
        return Response({
            'success': True,
            'data': data
        })


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for alert operations.
    """
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return alerts for the current user's organization."""
        user = self.request.user
        if hasattr(user, 'organization'):
            queryset = Alert.objects.filter(
                organization=user.organization
            )
            
            # Filter by acknowledgement status
            acknowledged = self.request.query_params.get('acknowledged')
            if acknowledged is not None:
                queryset = queryset.filter(
                    is_acknowledged=acknowledged.lower() == 'true'
                )
            
            # Filter by severity
            severity = self.request.query_params.get('severity')
            if severity:
                queryset = queryset.filter(severity=severity)
            
            # Filter by alert type
            alert_type = self.request.query_params.get('type')
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)
            
            # Filter by satellite image
            image_id = self.request.query_params.get('image')
            if image_id:
                queryset = queryset.filter(satellite_image_id=image_id)
            
            return queryset
        return Alert.objects.none()

    def list(self, request, *args, **kwargs):
        """List all alerts for the user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Count unacknowledged alerts by severity
        unacknowledged = queryset.filter(is_acknowledged=False)
        severity_counts = {
            'critical': unacknowledged.filter(severity='critical').count(),
            'high': unacknowledged.filter(severity='high').count(),
            'medium': unacknowledged.filter(severity='medium').count(),
            'low': unacknowledged.filter(severity='low').count(),
        }
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'unacknowledged_count': unacknowledged.count(),
            'severity_counts': severity_counts,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='acknowledge')
    def acknowledge_alerts(self, request):
        """Acknowledge one or more alerts."""
        serializer = AlertAcknowledgeSerializer(data=request.data)
        if serializer.is_valid():
            alert_ids = serializer.validated_data['alert_ids']
            alerts = self.get_queryset().filter(
                id__in=alert_ids,
                is_acknowledged=False
            )
            
            count = alerts.update(
                is_acknowledged=True,
                acknowledged_at=timezone.now(),
                acknowledged_by=request.user
            )
            
            return Response({
                'success': True,
                'message': f'{count} alert(s) acknowledged successfully.',
                'count': count
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_single(self, request, pk=None):
        """Acknowledge a single alert."""
        alert = self.get_object()
        if alert.is_acknowledged:
            return Response({
                'success': False,
                'message': 'Alert is already acknowledged.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alert acknowledged successfully.',
            'data': AlertSerializer(alert).data
        })

    @action(detail=False, methods=['get'], url_path='unacknowledged')
    def unacknowledged(self, request):
        """Get all unacknowledged alerts."""
        queryset = self.get_queryset().filter(is_acknowledged=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='critical')
    def critical_alerts(self, request):
        """Get all critical unacknowledged alerts."""
        queryset = self.get_queryset().filter(
            is_acknowledged=False,
            severity__in=['critical', 'high']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

