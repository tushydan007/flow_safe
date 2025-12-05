"""
Celery tasks for image analysis.
"""

import os
import logging
from datetime import datetime
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('analysis')


def send_websocket_update(organization_id: int, event_type: str, data: dict):
    """
    Send WebSocket update to organization's channel.
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'pipeline_{organization_id}',
            {
                'type': event_type,
                'data': data
            }
        )
    except Exception as e:
        logger.warning(f"WebSocket send failed: {e}")


def send_alert_notification(organization_id: int, alert_data: dict):
    """
    Send alert notification via WebSocket.
    """
    try:
        channel_layer = get_channel_layer()
        event_type = 'critical_alert' if alert_data.get('severity') in ['critical', 'high'] else 'new_alert'
        async_to_sync(channel_layer.group_send)(
            f'alerts_{organization_id}',
            {
                'type': event_type,
                'data': alert_data
            }
        )
    except Exception as e:
        logger.warning(f"Alert notification failed: {e}")


@shared_task(bind=True, max_retries=3)
def process_satellite_image(self, image_id: int):
    """
    Process a satellite image: extract metadata and convert to COG.
    """
    from pipeline.models import SatelliteImage
    from .processors import COGConverter
    
    try:
        image = SatelliteImage.objects.get(id=image_id)
        image.status = 'processing'
        image.save(update_fields=['status'])
        
        org_id = image.organization.pk
        
        send_websocket_update(org_id, 'image_update', {
            'id': image_id,
            'status': 'processing',
            'message': 'Starting image processing...'
        })
        
        # Get file path
        if not image.original_file:
            raise ValueError("No image file uploaded")
        
        input_path = image.original_file.path
        
        # Extract metadata
        converter = COGConverter()
        metadata = converter.extract_metadata(input_path)
        
        if metadata:
            image.width = metadata.get('width')
            image.height = metadata.get('height')
            image.bands = metadata.get('bands')
            image.crs = metadata.get('crs')
            image.bounds = metadata.get('bounds')
            image.center = metadata.get('center')
            image.resolution = metadata.get('resolution')
        
        send_websocket_update(org_id, 'image_update', {
            'id': image_id,
            'status': 'processing',
            'message': 'Converting to Cloud Optimized GeoTIFF...'
        })
        
        # Convert to COG
        output_dir = os.path.join(settings.MEDIA_ROOT, 'cog_images', str(org_id))
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.basename(input_path)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_cog.tif"
        output_path = os.path.join(output_dir, output_filename)
        
        def progress_callback(progress, message):
            send_websocket_update(org_id, 'image_update', {
                'id': image_id,
                'status': 'processing',
                'progress': progress,
                'message': message
            })
        
        result = converter.convert(input_path, output_path, progress_callback)
        
        if result['success']:
            # Save COG path relative to MEDIA_ROOT
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            image.cog_file = relative_path
            image.status = 'ready'
            
            send_websocket_update(org_id, 'image_update', {
                'id': image_id,
                'status': 'ready',
                'message': 'Image processing complete!'
            })
        else:
            image.status = 'error'
            image.error_message = result.get('error', 'Unknown error during processing')
            
            send_websocket_update(org_id, 'image_update', {
                'id': image_id,
                'status': 'error',
                'message': image.error_message
            })
        
        image.save()
        return {'success': True, 'image_id': image_id}
        
    except SatelliteImage.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return {'success': False, 'error': 'Image not found'}
    except Exception as e:
        logger.exception(f"Error processing image {image_id}: {e}")
        try:
            image = SatelliteImage.objects.get(id=image_id)
            image.status = 'error'
            image.error_message = str(e)
            image.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        
        self.retry(countdown=60, exc=e)


@shared_task(bind=True)
def convert_to_cog(self, image_id: int):
    """
    Convert a satellite image to Cloud Optimized GeoTIFF.
    """
    return process_satellite_image(image_id)


@shared_task(bind=True, max_retries=2)
def run_all_analyses(self, image_id: int):
    """
    Run all analysis types on a satellite image.
    """
    from pipeline.models import SatelliteImage
    from .models import AnalysisResult
    
    try:
        image = SatelliteImage.objects.get(id=image_id)
        
        if image.status != 'ready':
            logger.warning(f"Image {image_id} not ready for analysis")
            return {'success': False, 'error': 'Image not ready'}
        
        org_id = image.organization.pk
        
        # Create analysis tasks
        analysis_types = ['ndvi', 'change', 'encroachment', 'emission', 'facility']
        
        for analysis_type in analysis_types:
            # Create or get analysis result record
            result, created = AnalysisResult.objects.get_or_create(
                satellite_image=image,
                analysis_type=analysis_type,
                defaults={'status': 'pending'}
            )
            
            if not created and result.status == 'completed':
                continue  # Skip already completed analyses
            
            # Queue individual analysis task
            run_analysis.delay(image_id, analysis_type)
        
        send_websocket_update(org_id, 'analysis_progress', {
            'image_id': image_id,
            'message': 'All analyses queued',
            'types': analysis_types
        })
        
        return {'success': True, 'image_id': image_id, 'analyses': analysis_types}
        
    except SatelliteImage.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return {'success': False, 'error': 'Image not found'}
    except Exception as e:
        logger.exception(f"Error queuing analyses for image {image_id}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(bind=True, max_retries=2, time_limit=1800)
def run_analysis(self, image_id: int, analysis_type: str):
    """
    Run a specific analysis on a satellite image.
    """
    from pipeline.models import SatelliteImage, Alert
    from .models import (
        AnalysisResult, LeakDetection, ChangeDetection,
        EncroachmentDetection, EmissionDetection, FacilityMonitoring
    )
    from .processors import (
        NDVIProcessor, ChangeDetectionProcessor, EncroachmentProcessor,
        EmissionProcessor, FacilityProcessor
    )
    
    start_time = datetime.now()
    
    try:
        image = SatelliteImage.objects.get(id=image_id)
        org_id = image.organization.pk
        
        # Get or create analysis result
        result, _ = AnalysisResult.objects.get_or_create(
            satellite_image=image,
            analysis_type=analysis_type,
            defaults={'status': 'pending'}
        )
        
        result.status = 'processing'
        result.started_at = timezone.now()
        result.save(update_fields=['status', 'started_at'])
        
        # Get image path
        image_path = image.cog_file.path if image.cog_file else image.original_file.path
        
        def progress_callback(progress, message):
            result.progress = progress
            result.save(update_fields=['progress'])
            
            send_websocket_update(org_id, 'analysis_progress', {
                'image_id': image_id,
                'analysis_type': analysis_type,
                'progress': progress,
                'message': message
            })
        
        # Select processor
        processors = {
            'ndvi': NDVIProcessor,
            'change': ChangeDetectionProcessor,
            'encroachment': EncroachmentProcessor,
            'emission': EmissionProcessor,
            'facility': FacilityProcessor,
        }
        
        processor_class = processors.get(analysis_type)
        if not processor_class:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        processor = processor_class(progress_callback=progress_callback)
        
        # Run analysis
        analysis_result = processor.process_image(image_path)
        
        if 'error' in analysis_result:
            result.status = 'failed'
            result.error_message = analysis_result['error']
            result.save()
            return {'success': False, 'error': analysis_result['error']}
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Save results
        result.status = 'completed'
        result.progress = 100
        result.result_data = analysis_result
        result.summary = analysis_result.get('summary', '')
        result.processing_time_seconds = processing_time
        result.chunks_total = analysis_result.get('metadata', {}).get('chunks_processed', 0)
        result.chunks_processed = result.chunks_total
        result.completed_at = timezone.now()
        
        # Determine overall severity
        severity_counts = analysis_result.get('severity_counts', {})
        if severity_counts.get('critical', 0) > 0:
            result.severity = 'critical'
        elif severity_counts.get('high', 0) > 0:
            result.severity = 'high'
        elif severity_counts.get('medium', 0) > 0:
            result.severity = 'medium'
        else:
            result.severity = 'low'
        
        # Generate GeoJSON for map display
        result.result_geojson = _generate_result_geojson(analysis_result)
        
        result.save()
        
        # Create detailed detection records and alerts
        _save_detections(result, analysis_result, image)
        
        # Check if all analyses are complete
        all_complete = not AnalysisResult.objects.filter(
            satellite_image=image,
            status__in=['pending', 'processing']
        ).exists()
        
        if all_complete:
            image.is_analyzed = True
            image.analysis_completed_at = timezone.now()
            image.save(update_fields=['is_analyzed', 'analysis_completed_at'])
            
            send_websocket_update(org_id, 'analysis_complete', {
                'image_id': image_id,
                'message': 'All analyses complete'
            })
        
        return {
            'success': True,
            'image_id': image_id,
            'analysis_type': analysis_type,
            'processing_time': processing_time
        }
        
    except Exception as e:
        logger.exception(f"Error running {analysis_type} analysis on image {image_id}: {e}")
        
        try:
            result = AnalysisResult.objects.get(
                satellite_image_id=image_id,
                analysis_type=analysis_type
            )
            result.status = 'failed'
            result.error_message = str(e)
            result.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        
        self.retry(countdown=120, exc=e)


def _generate_result_geojson(analysis_result: dict) -> dict:
    """
    Generate GeoJSON from analysis results for map display.
    """
    features = []
    detections = analysis_result.get('detections', [])
    
    for detection in detections:
        location = detection.get('location', {})
        if not location:
            continue
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [location.get('lng', 0), location.get('lat', 0)]
            },
            'properties': {
                'severity': detection.get('severity', 'low'),
                **{k: v for k, v in detection.items() if k not in ['location', 'pixel_location']}
            }
        }
        features.append(feature)
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def _save_detections(result: 'AnalysisResult', analysis_result: dict, image: 'SatelliteImage'):
    """
    Save detection records and create alerts for significant findings.
    """
    from pipeline.models import Alert
    from .models import (
        LeakDetection, ChangeDetection, EncroachmentDetection,
        EmissionDetection, FacilityMonitoring
    )
    
    detections = analysis_result.get('detections', [])
    alert_type_map = {
        'ndvi': 'leak',
        'change': 'change',
        'encroachment': 'encroachment',
        'emission': 'emission',
        'facility': 'facility',
    }
    
    for detection in detections:
        severity = detection.get('severity', 'low')
        
        # Create specific detection record based on analysis type
        if result.analysis_type == 'ndvi':
            LeakDetection.objects.create(
                analysis_result=result,
                location=detection.get('location', {}),
                ndvi_value=detection.get('ndvi_value', 0),
                confidence=1.0,
                extent_sqm=detection.get('pixel_count', 0) * 100,  # Approximate
                severity=severity,
                description=f"Potential leak detected with NDVI value of {detection.get('ndvi_value', 0):.3f}"
            )
        
        elif result.analysis_type == 'change':
            ChangeDetection.objects.create(
                analysis_result=result,
                location=detection.get('location', {}),
                change_type=detection.get('change_type', 'unknown'),
                change_percentage=detection.get('change_percentage', 0),
                confidence=1.0,
                severity=severity,
                description=f"{detection.get('change_type', 'Unknown')} change detected"
            )
        
        elif result.analysis_type == 'encroachment':
            EncroachmentDetection.objects.create(
                analysis_result=result,
                location=detection.get('location', {}),
                object_type=detection.get('object_type', 'other'),
                object_label=detection.get('object_label', 'unknown'),
                confidence=detection.get('confidence', 0),
                bounding_box=detection.get('bounding_box', []),
                distance_to_pipeline_m=detection.get('distance_to_pipeline_m'),
                severity=severity,
                description=f"{detection.get('object_label', 'Object')} detected near pipeline"
            )
        
        elif result.analysis_type == 'emission':
            EmissionDetection.objects.create(
                analysis_result=result,
                location=detection.get('location', {}),
                emission_type=detection.get('emission_type', 'other'),
                intensity=detection.get('intensity', 0),
                confidence=1.0,
                estimated_volume=detection.get('estimated_volume'),
                severity=severity,
                description=f"{detection.get('emission_type', 'Emission')} anomaly detected"
            )
        
        elif result.analysis_type == 'facility':
            FacilityMonitoring.objects.create(
                analysis_result=result,
                location=detection.get('location', {}),
                facility_type=detection.get('facility_type', 'other'),
                condition=detection.get('condition', 'normal'),
                confidence=detection.get('confidence', 0),
                area_sqm=detection.get('area_sqm'),
                severity=severity,
                description=f"{detection.get('facility_type', 'Facility')} - {detection.get('condition', 'unknown')} condition"
            )
        
        # Create alert for high/critical severity findings
        if severity in ['critical', 'high']:
            alert_type = alert_type_map.get(result.analysis_type, 'system')
            
            alert = Alert.objects.create(
                organization=image.organization,
                satellite_image=image,
                pipeline=image.pipeline,
                alert_type=alert_type,
                severity=severity,
                title=f"{alert_type.replace('_', ' ').title()} Alert",
                description=f"Analysis detected a {severity} severity issue. {detection.get('description', 'Please investigate.')}",
                location=detection.get('location'),
            )
            
            # Send real-time alert notification
            send_alert_notification(image.organization.pk, {
                'id': alert.id,
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'description': alert.description,
                'location': alert.location,
                'created_at': alert.created_at.isoformat(),
            })

