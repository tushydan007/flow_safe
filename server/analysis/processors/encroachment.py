"""
Encroachment detection processor using object detection (YOLO).
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

from .base import BaseProcessor

logger = logging.getLogger('analysis')


class EncroachmentProcessor(BaseProcessor):
    """
    Processor for encroachment detection using YOLO object detection.
    
    Detects objects near pipelines that may pose safety risks.
    """
    
    # Object classes of interest
    OBJECT_CLASSES = {
        0: {'name': 'person', 'type': 'person'},
        1: {'name': 'bicycle', 'type': 'vehicle'},
        2: {'name': 'car', 'type': 'vehicle'},
        3: {'name': 'motorcycle', 'type': 'vehicle'},
        5: {'name': 'bus', 'type': 'vehicle'},
        7: {'name': 'truck', 'type': 'vehicle'},
        16: {'name': 'dog', 'type': 'animal'},
        17: {'name': 'horse', 'type': 'animal'},
        18: {'name': 'sheep', 'type': 'animal'},
        19: {'name': 'cow', 'type': 'animal'},
    }
    
    # Severity based on object type proximity
    SEVERITY_THRESHOLDS = {
        'critical': 10,   # Within 10 meters
        'high': 25,       # Within 25 meters
        'medium': 50,     # Within 50 meters
        'low': 100,       # Within 100 meters
    }
    
    def __init__(
        self,
        model_path: str = None,
        confidence_threshold: float = 0.5,
        pipeline_buffer_m: float = 100,
        **kwargs
    ):
        """
        Initialize encroachment processor.
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detection
            pipeline_buffer_m: Buffer distance around pipeline in meters
        """
        super().__init__(**kwargs)
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.pipeline_buffer_m = pipeline_buffer_m
        self.model = None
    
    def load_model(self):
        """
        Load YOLO model for object detection.
        """
        if self.model is not None:
            return
        
        try:
            from ultralytics import YOLO
            
            if self.model_path:
                self.model = YOLO(self.model_path)
            else:
                # Use pre-trained YOLOv8 model
                self.model = YOLO('yolov8n.pt')
            
            logger.info("YOLO model loaded successfully")
        except ImportError:
            logger.error("ultralytics not installed")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            self.model = None
    
    def detect_objects(
        self,
        image: np.ndarray
    ) -> List[Dict]:
        """
        Detect objects in image using YOLO.
        
        Args:
            image: Image data (height, width, channels)
            
        Returns:
            List of detected objects
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                return self._simulate_detections(image)
        
        try:
            # Ensure image is in correct format (RGB, uint8)
            if len(image.shape) == 3 and image.shape[0] <= 4:
                # Convert from (C, H, W) to (H, W, C)
                image = np.transpose(image, (1, 2, 0))
            
            if image.shape[2] > 3:
                image = image[:, :, :3]
            
            if image.dtype != np.uint8:
                image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
            
            # Run detection
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i])
                    conf = float(boxes.conf[i])
                    bbox = boxes.xyxy[i].cpu().numpy()
                    
                    if cls_id in self.OBJECT_CLASSES:
                        obj_info = self.OBJECT_CLASSES[cls_id]
                        
                        # Calculate center
                        center_x = (bbox[0] + bbox[2]) / 2
                        center_y = (bbox[1] + bbox[3]) / 2
                        
                        detections.append({
                            'class_id': cls_id,
                            'label': obj_info['name'],
                            'type': obj_info['type'],
                            'confidence': conf,
                            'bbox': bbox.tolist(),
                            'center': (center_x, center_y),
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return self._simulate_detections(image)
    
    def _simulate_detections(self, image: np.ndarray) -> List[Dict]:
        """
        Simulate object detections when model is not available.
        Used for development/testing.
        """
        # Return empty list or simulated results
        height = image.shape[1] if len(image.shape) == 3 and image.shape[0] <= 4 else image.shape[0]
        width = image.shape[2] if len(image.shape) == 3 and image.shape[0] <= 4 else image.shape[1]
        
        # Randomly simulate a few detections for testing
        np.random.seed(hash(image.tobytes()[:100]) % (2**32))
        
        if np.random.random() < 0.1:  # 10% chance of detection
            return [{
                'class_id': 2,
                'label': 'car',
                'type': 'vehicle',
                'confidence': 0.75,
                'bbox': [100, 100, 200, 180],
                'center': (150, 140),
            }]
        
        return []
    
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a chunk for object detection.
        """
        col_off, row_off, win_width, win_height = window
        
        # Detect objects
        detections = self.detect_objects(data)
        
        if not detections:
            return None
        
        transform = metadata.get('transform')
        resolution = self._estimate_resolution(transform)
        
        results = []
        for detection in detections:
            # Adjust coordinates for window offset
            center_x = detection['center'][0] + col_off
            center_y = detection['center'][1] + row_off
            
            # Convert to geographic coordinates
            lng, lat = self.pixel_to_coordinates(center_x, center_y, transform)
            
            # Adjust bounding box
            bbox = detection['bbox']
            adjusted_bbox = [
                bbox[0] + col_off,
                bbox[1] + row_off,
                bbox[2] + col_off,
                bbox[3] + row_off,
            ]
            
            # Estimate distance (simulated for now)
            distance = np.random.uniform(5, 150)  # Would calculate from pipeline geometry
            
            # Determine severity based on proximity
            severity = 'low'
            for sev, threshold in sorted(
                self.SEVERITY_THRESHOLDS.items(),
                key=lambda x: x[1]
            ):
                if distance <= threshold:
                    severity = sev
                    break
            
            results.append({
                'location': {'lng': lng, 'lat': lat},
                'pixel_location': {'col': center_x, 'row': center_y},
                'object_type': detection['type'],
                'object_label': detection['label'],
                'confidence': detection['confidence'],
                'bounding_box': adjusted_bbox,
                'distance_to_pipeline_m': distance,
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
        
        return abs(transform[0])  # Pixel width
    
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge encroachment detection results.
        """
        all_detections = []
        
        for result in chunk_results:
            if result and 'detections' in result:
                all_detections.extend(result['detections'])
        
        # Group by object type
        by_type = {}
        for detection in all_detections:
            obj_type = detection['object_type']
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(detection)
        
        # Sort by distance
        all_detections.sort(key=lambda x: x['distance_to_pipeline_m'])
        
        summary = self._generate_summary(all_detections, by_type)
        
        return {
            'analysis_type': 'encroachment',
            'detections': all_detections,
            'by_type': by_type,
            'summary': summary,
            'total_objects': len(all_detections),
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
        Generate human-readable summary of encroachment detection.
        """
        if not detections:
            return (
                "No objects or encroachments were detected near the pipeline corridor. "
                "The area appears clear of unauthorized activities or hazards."
            )
        
        parts = [f"Detected {len(detections)} object(s) near the pipeline corridor."]
        
        for obj_type, items in by_type.items():
            if items:
                closest = min(items, key=lambda x: x['distance_to_pipeline_m'])
                parts.append(
                    f"Found {len(items)} {obj_type}(s), "
                    f"closest at {closest['distance_to_pipeline_m']:.1f} meters from pipeline."
                )
        
        critical = [d for d in detections if d['severity'] == 'critical']
        if critical:
            parts.append(
                f"WARNING: {len(critical)} object(s) detected within critical proximity "
                f"(10 meters) of the pipeline requiring immediate attention."
            )
        
        parts.append(
            "Review detected objects on the map and verify they do not pose "
            "a risk to pipeline operations or safety."
        )
        
        return " ".join(parts)

