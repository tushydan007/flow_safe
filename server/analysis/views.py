"""
Views for analysis-related operations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from pipeline.models import SatelliteImage
from .models import (
    AnalysisResult, LeakDetection, ChangeDetection,
    EncroachmentDetection, EmissionDetection, FacilityMonitoring
)
from .serializers import (
    AnalysisResultSerializer,
    AnalysisResultDetailSerializer,
    AnalysisResultListSerializer,
    RunAnalysisSerializer,
    LeakDetectionSerializer,
    ChangeDetectionSerializer,
    EncroachmentDetectionSerializer,
    EmissionDetectionSerializer,
    FacilityMonitoringSerializer,
)
from .tasks import run_all_analyses, run_analysis


class AnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing analysis results.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnalysisResultDetailSerializer
        if self.action == 'list':
            return AnalysisResultListSerializer
        return AnalysisResultSerializer

    def get_queryset(self):
        """Return analysis results for the current user's organization."""
        user = self.request.user
        if hasattr(user, 'organization'):
            queryset = AnalysisResult.objects.filter(
                satellite_image__organization=user.organization
            )
            
            # Filter by image
            image_id = self.request.query_params.get('image')
            if image_id:
                queryset = queryset.filter(satellite_image_id=image_id)
            
            # Filter by analysis type
            analysis_type = self.request.query_params.get('type')
            if analysis_type:
                queryset = queryset.filter(analysis_type=analysis_type)
            
            # Filter by status
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            return queryset.select_related('satellite_image')
        return AnalysisResult.objects.none()

    def list(self, request, *args, **kwargs):
        """List all analysis results for the user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """Get detailed analysis result with all detections."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='run')
    def run_analysis(self, request):
        """
        Run analysis on a satellite image.
        """
        image_id = request.data.get('image_id')
        if not image_id:
            return Response({
                'success': False,
                'error': 'image_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify image belongs to user's organization
        try:
            image = SatelliteImage.objects.get(
                id=image_id,
                organization=request.user.organization
            )
        except SatelliteImage.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Image not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if image.status != 'ready':
            return Response({
                'success': False,
                'error': 'Image is not ready for analysis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RunAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            analysis_types = serializer.validated_data.get('analysis_types', ['all'])
            
            if 'all' in analysis_types:
                run_all_analyses.delay(image_id)
                message = 'All analyses queued'
            else:
                for atype in analysis_types:
                    run_analysis.delay(image_id, atype)
                message = f'{len(analysis_types)} analysis/analyses queued'
            
            return Response({
                'success': True,
                'message': message,
                'image_id': image_id
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-image/(?P<image_id>[0-9]+)')
    def by_image(self, request, image_id=None):
        """
        Get all analysis results for a specific image.
        """
        queryset = self.get_queryset().filter(satellite_image_id=image_id)
        serializer = AnalysisResultSerializer(queryset, many=True)
        
        # Calculate summary
        total_detections = 0
        severity_summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for result in queryset:
            if result.result_data:
                counts = result.result_data.get('severity_counts', {})
                for severity, count in counts.items():
                    severity_summary[severity] = severity_summary.get(severity, 0) + count
                    total_detections += count
        
        return Response({
            'success': True,
            'image_id': image_id,
            'count': queryset.count(),
            'total_detections': total_detections,
            'severity_summary': severity_summary,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='geojson')
    def geojson(self, request, pk=None):
        """
        Get GeoJSON for an analysis result.
        """
        instance = self.get_object()
        if instance.result_geojson:
            return Response({
                'success': True,
                'data': instance.result_geojson
            })
        return Response({
            'success': False,
            'message': 'GeoJSON not available'
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Get analysis summary for all images.
        """
        queryset = self.get_queryset()
        
        # Group by image
        image_ids = queryset.values_list('satellite_image_id', flat=True).distinct()
        
        summaries = []
        for image_id in image_ids:
            try:
                image = SatelliteImage.objects.get(id=image_id)
                results = queryset.filter(satellite_image_id=image_id)
                
                total_alerts = image.alerts.count()
                critical_alerts = image.alerts.filter(
                    is_acknowledged=False,
                    severity__in=['critical', 'high']
                ).count()
                
                # Determine overall status
                statuses = list(results.values_list('status', flat=True))
                if 'failed' in statuses:
                    overall_status = 'error'
                elif 'processing' in statuses:
                    overall_status = 'processing'
                elif 'pending' in statuses:
                    overall_status = 'pending'
                elif all(s == 'completed' for s in statuses):
                    overall_status = 'completed'
                else:
                    overall_status = 'partial'
                
                summaries.append({
                    'image_id': image_id,
                    'image_name': image.name,
                    'acquisition_date': image.acquisition_date,
                    'is_analyzed': image.is_analyzed,
                    'analysis_results': AnalysisResultListSerializer(results, many=True).data,
                    'total_alerts': total_alerts,
                    'critical_alerts': critical_alerts,
                    'overall_status': overall_status,
                })
            except SatelliteImage.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'count': len(summaries),
            'data': summaries
        })


class LeakDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for leak detections."""
    
    serializer_class = LeakDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return LeakDetection.objects.filter(
                analysis_result__satellite_image__organization=user.organization
            )
        return LeakDetection.objects.none()


class ChangeDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for change detections."""
    
    serializer_class = ChangeDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return ChangeDetection.objects.filter(
                analysis_result__satellite_image__organization=user.organization
            )
        return ChangeDetection.objects.none()


class EncroachmentDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for encroachment detections."""
    
    serializer_class = EncroachmentDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return EncroachmentDetection.objects.filter(
                analysis_result__satellite_image__organization=user.organization
            )
        return EncroachmentDetection.objects.none()


class EmissionDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for emission detections."""
    
    serializer_class = EmissionDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return EmissionDetection.objects.filter(
                analysis_result__satellite_image__organization=user.organization
            )
        return EmissionDetection.objects.none()


class FacilityMonitoringViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for facility monitoring."""
    
    serializer_class = FacilityMonitoringSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'organization'):
            return FacilityMonitoring.objects.filter(
                analysis_result__satellite_image__organization=user.organization
            )
        return FacilityMonitoring.objects.none()

