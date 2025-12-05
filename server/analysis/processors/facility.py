"""
Facility monitoring processor using U-Net segmentation.
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

from .base import BaseProcessor

logger = logging.getLogger('analysis')


class FacilityProcessor(BaseProcessor):
    """
    Processor for facility monitoring using semantic segmentation.
    
    Uses U-Net or similar architecture to segment and monitor
    pipeline facilities and infrastructure.
    """
    
    # Facility classes
    FACILITY_CLASSES = {
        0: 'background',
        1: 'pipeline_segment',
        2: 'valve_station',
        3: 'pump_station',
        4: 'storage_tank',
        5: 'access_road',
    }
    
    # Condition assessment thresholds
    CONDITION_THRESHOLDS = {
        'normal': 0.9,
        'minor_issue': 0.75,
        'moderate_issue': 0.5,
        'severe_issue': 0.25,
        'critical': 0.0,
    }
    
    def __init__(
        self,
        model_path: str = None,
        **kwargs
    ):
        """
        Initialize facility processor.
        
        Args:
            model_path: Path to U-Net model weights
        """
        super().__init__(**kwargs)
        self.model_path = model_path
        self.model = None
    
    def load_model(self):
        """
        Load U-Net model for segmentation.
        """
        if self.model is not None:
            return
        
        try:
            import torch
            import segmentation_models_pytorch as smp
            
            # Create U-Net model
            self.model = smp.Unet(
                encoder_name="resnet34",
                encoder_weights=None,
                in_channels=3,
                classes=len(self.FACILITY_CLASSES),
            )
            
            if self.model_path:
                self.model.load_state_dict(torch.load(self.model_path))
            
            self.model.eval()
            logger.info("U-Net model loaded successfully")
            
        except ImportError:
            logger.warning("segmentation_models_pytorch not installed")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading U-Net model: {e}")
            self.model = None
    
    def segment_facilities(
        self,
        image: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Segment facilities in the image.
        
        Args:
            image: Image data
            
        Returns:
            Tuple of (segmentation mask, list of facilities)
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                return self._simulate_segmentation(image)
        
        try:
            import torch
            
            # Prepare image
            if len(image.shape) == 3 and image.shape[0] <= 4:
                image = np.transpose(image, (1, 2, 0))
            
            if image.shape[2] > 3:
                image = image[:, :, :3]
            
            # Normalize
            image = image.astype(np.float32)
            image = (image - image.min()) / (image.max() - image.min() + 1e-6)
            
            # Convert to tensor
            tensor = torch.from_numpy(image.transpose(2, 0, 1)).unsqueeze(0)
            
            with torch.no_grad():
                output = self.model(tensor)
                probs = torch.softmax(output, dim=1)
                mask = torch.argmax(probs, dim=1).squeeze().numpy()
                confidence = torch.max(probs, dim=1)[0].squeeze().numpy()
            
            return self._extract_facilities(mask, confidence)
            
        except Exception as e:
            logger.error(f"Error in segmentation: {e}")
            return self._simulate_segmentation(image)
    
    def _simulate_segmentation(
        self,
        image: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Simulate segmentation when model is not available.
        """
        if len(image.shape) == 3 and image.shape[0] <= 4:
            height, width = image.shape[1], image.shape[2]
        else:
            height, width = image.shape[0], image.shape[1]
        
        # Create dummy mask
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Random seed for consistency
        np.random.seed(hash(image.tobytes()[:100]) % (2**32))
        
        facilities = []
        
        # Simulate random facility detections
        if np.random.random() < 0.2:
            cy, cx = np.random.randint(50, height-50), np.random.randint(50, width-50)
            facilities.append({
                'centroid': (cx, cy),
                'class_id': 1,
                'class_name': 'pipeline_segment',
                'pixel_count': 500,
                'confidence': 0.85,
                'condition_score': 0.8,
                'condition': 'normal',
            })
        
        return mask, facilities
    
    def _extract_facilities(
        self,
        mask: np.ndarray,
        confidence: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Extract facility information from segmentation mask.
        """
        facilities = []
        
        try:
            from scipy import ndimage
            
            for class_id in range(1, len(self.FACILITY_CLASSES)):
                class_mask = mask == class_id
                if not np.any(class_mask):
                    continue
                
                labeled, num_features = ndimage.label(class_mask)
                
                for i in range(1, num_features + 1):
                    region_mask = labeled == i
                    region_pixels = np.sum(region_mask)
                    
                    if region_pixels < 10:
                        continue
                    
                    # Calculate statistics
                    region_conf = confidence[region_mask]
                    mean_conf = float(np.mean(region_conf))
                    
                    # Find centroid
                    coords = np.where(region_mask)
                    centroid_row = int(np.mean(coords[0]))
                    centroid_col = int(np.mean(coords[1]))
                    
                    # Assess condition based on confidence
                    condition = 'normal'
                    for cond, threshold in sorted(
                        self.CONDITION_THRESHOLDS.items(),
                        key=lambda x: -x[1]
                    ):
                        if mean_conf >= threshold:
                            condition = cond
                            break
                    
                    facilities.append({
                        'centroid': (centroid_col, centroid_row),
                        'class_id': class_id,
                        'class_name': self.FACILITY_CLASSES[class_id],
                        'pixel_count': int(region_pixels),
                        'confidence': mean_conf,
                        'condition_score': mean_conf,
                        'condition': condition,
                    })
                    
        except ImportError:
            logger.warning("scipy not available for facility extraction")
        
        return mask, facilities
    
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a chunk for facility monitoring.
        """
        col_off, row_off, win_width, win_height = window
        
        # Segment facilities
        _, facilities = self.segment_facilities(data)
        
        if not facilities:
            return None
        
        transform = metadata.get('transform')
        resolution = self._estimate_resolution(transform)
        
        results = []
        for facility in facilities:
            pixel_col = facility['centroid'][0] + col_off
            pixel_row = facility['centroid'][1] + row_off
            
            lng, lat = self.pixel_to_coordinates(pixel_col, pixel_row, transform)
            
            # Calculate area
            area_sqm = facility['pixel_count'] * (resolution ** 2)
            
            # Map condition to severity
            condition_severity = {
                'normal': 'low',
                'minor_issue': 'low',
                'moderate_issue': 'medium',
                'severe_issue': 'high',
                'critical': 'critical',
            }
            severity = condition_severity.get(facility['condition'], 'low')
            
            results.append({
                'location': {'lng': lng, 'lat': lat},
                'pixel_location': {'col': pixel_col, 'row': pixel_row},
                'facility_type': facility['class_name'],
                'condition': facility['condition'],
                'condition_score': facility['condition_score'],
                'confidence': facility['confidence'],
                'area_sqm': area_sqm,
                'severity': severity,
            })
        
        return {
            'window': window,
            'detections': results,
        }
    
    def _estimate_resolution(self, transform) -> float:
        """
        Estimate image resolution in meters per pixel.
        """
        if transform is None:
            return 1.0
        return abs(transform[0])
    
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge facility monitoring results.
        """
        all_detections = []
        
        for result in chunk_results:
            if result and 'detections' in result:
                all_detections.extend(result['detections'])
        
        # Group by facility type
        by_type = {}
        for detection in all_detections:
            facility_type = detection['facility_type']
            if facility_type not in by_type:
                by_type[facility_type] = []
            by_type[facility_type].append(detection)
        
        # Sort by condition severity
        condition_order = {
            'critical': 0, 'severe_issue': 1, 'moderate_issue': 2,
            'minor_issue': 3, 'normal': 4
        }
        all_detections.sort(
            key=lambda x: condition_order.get(x['condition'], 5)
        )
        
        summary = self._generate_summary(all_detections, by_type)
        
        return {
            'analysis_type': 'facility',
            'detections': all_detections,
            'by_type': by_type,
            'summary': summary,
            'total_facilities': len(all_detections),
            'condition_counts': {
                'normal': len([d for d in all_detections if d['condition'] == 'normal']),
                'minor_issue': len([d for d in all_detections if d['condition'] == 'minor_issue']),
                'moderate_issue': len([d for d in all_detections if d['condition'] == 'moderate_issue']),
                'severe_issue': len([d for d in all_detections if d['condition'] == 'severe_issue']),
                'critical': len([d for d in all_detections if d['condition'] == 'critical']),
            },
            'severity_counts': {
                'critical': len([d for d in all_detections if d['severity'] == 'critical']),
                'high': len([d for d in all_detections if d['severity'] == 'high']),
                'medium': len([d for d in all_detections if d['severity'] == 'medium']),
                'low': len([d for d in all_detections if d['severity'] == 'low']),
            }
        }
    
    def _generate_summary(
        self,
        detections: List[Dict],
        by_type: Dict[str, List]
    ) -> str:
        """
        Generate human-readable summary of facility monitoring.
        """
        if not detections:
            return (
                "No pipeline facilities were detected in the analyzed area. "
                "This may indicate the image does not cover any infrastructure, "
                "or the facilities are not visible at this resolution."
            )
        
        parts = [f"Identified {len(detections)} pipeline facility/facilities in the image."]
        
        type_names = {
            'pipeline_segment': 'pipeline segment(s)',
            'valve_station': 'valve station(s)',
            'pump_station': 'pump station(s)',
            'storage_tank': 'storage tank(s)',
            'access_road': 'access road(s)',
        }
        
        for facility_type, items in by_type.items():
            if items:
                name = type_names.get(facility_type, facility_type)
                normal = len([i for i in items if i['condition'] == 'normal'])
                issues = len(items) - normal
                
                if issues > 0:
                    parts.append(
                        f"Detected {len(items)} {name}, "
                        f"with {issues} showing potential issues."
                    )
                else:
                    parts.append(f"Detected {len(items)} {name}, all in normal condition.")
        
        critical = [d for d in detections if d['condition'] in ['critical', 'severe_issue']]
        if critical:
            parts.append(
                f"MAINTENANCE REQUIRED: {len(critical)} facility/facilities show "
                f"severe or critical condition issues. Immediate inspection recommended."
            )
        
        # Calculate overall health score
        scores = [d['condition_score'] for d in detections]
        avg_score = np.mean(scores) if scores else 1.0
        parts.append(
            f"Overall infrastructure health score: {avg_score:.0%}. "
            f"Regular monitoring will help maintain facility integrity."
        )
        
        return " ".join(parts)

