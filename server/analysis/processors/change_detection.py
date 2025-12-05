"""
Change detection processor using image differencing.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

from .base import BaseProcessor

logger = logging.getLogger('analysis')


class ChangeDetectionProcessor(BaseProcessor):
    """
    Processor for change detection using image differencing.
    
    Compares the current image against baseline or historical data
    to detect significant changes in the landscape.
    """
    
    # Thresholds for change detection
    CHANGE_THRESHOLD = 0.15  # 15% change threshold
    SEVERITY_THRESHOLDS = {
        'critical': 0.5,
        'high': 0.35,
        'medium': 0.25,
        'low': 0.15,
    }
    
    def __init__(self, baseline_path: str = None, **kwargs):
        """
        Initialize change detection processor.
        
        Args:
            baseline_path: Path to baseline image for comparison
        """
        super().__init__(**kwargs)
        self.baseline_path = baseline_path
        self.baseline_data = None
    
    def calculate_normalized_difference(
        self,
        current: np.ndarray,
        baseline: np.ndarray
    ) -> np.ndarray:
        """
        Calculate normalized difference between current and baseline images.
        
        Args:
            current: Current image data
            baseline: Baseline image data
            
        Returns:
            Normalized difference array
        """
        current = current.astype(np.float32)
        baseline = baseline.astype(np.float32)
        
        # Calculate difference
        diff = current - baseline
        
        # Normalize by the baseline
        denominator = np.maximum(baseline, 1e-6)
        normalized_diff = diff / denominator
        
        return normalized_diff
    
    def classify_change(self, diff_value: float) -> str:
        """
        Classify the type of change based on difference value.
        
        Args:
            diff_value: Normalized difference value
            
        Returns:
            Change type classification
        """
        if diff_value > 0.3:
            return 'construction'
        elif diff_value > 0.1:
            return 'vegetation_gain'
        elif diff_value < -0.3:
            return 'erosion'
        elif diff_value < -0.1:
            return 'vegetation_loss'
        else:
            return 'unknown'
    
    def detect_changes(
        self,
        current: np.ndarray,
        baseline: np.ndarray = None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect significant changes in the image.
        
        Args:
            current: Current image data
            baseline: Baseline image data (optional)
            
        Returns:
            Tuple of (change mask, list of change regions)
        """
        # If no baseline, simulate by analyzing variance
        if baseline is None:
            # Use local variance as proxy for change detection
            mean_band = np.mean(current, axis=0)
            local_mean = np.zeros_like(mean_band)
            
            try:
                from scipy.ndimage import uniform_filter
                local_mean = uniform_filter(mean_band, size=50)
            except ImportError:
                local_mean = mean_band
            
            diff = np.abs(mean_band - local_mean) / np.maximum(local_mean, 1e-6)
        else:
            diff = np.mean(
                self.calculate_normalized_difference(current, baseline),
                axis=0
            )
        
        # Create change mask
        change_mask = np.abs(diff) > self.CHANGE_THRESHOLD
        
        # Find connected regions
        regions = []
        try:
            from scipy import ndimage
            labeled, num_features = ndimage.label(change_mask)
            
            for i in range(1, num_features + 1):
                region_mask = labeled == i
                region_pixels = np.sum(region_mask)
                
                if region_pixels < 25:  # Skip small regions
                    continue
                
                # Calculate region statistics
                region_diff = diff[region_mask]
                mean_change = float(np.mean(region_diff))
                max_change = float(np.max(np.abs(region_diff)))
                
                # Find centroid
                coords = np.where(region_mask)
                centroid_row = int(np.mean(coords[0]))
                centroid_col = int(np.mean(coords[1]))
                
                # Classify change type
                change_type = self.classify_change(mean_change)
                
                # Calculate severity
                severity = self.get_severity(abs(max_change), self.SEVERITY_THRESHOLDS)
                
                regions.append({
                    'centroid': (centroid_col, centroid_row),
                    'pixel_count': int(region_pixels),
                    'mean_change': mean_change,
                    'max_change': max_change,
                    'change_type': change_type,
                    'severity': severity,
                })
                
        except ImportError:
            logger.warning("scipy not available for region analysis")
        
        return change_mask, regions
    
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a chunk for change detection.
        """
        col_off, row_off, win_width, win_height = window
        
        # Detect changes
        _, changes = self.detect_changes(data, self.baseline_data)
        
        if not changes:
            return None
        
        transform = metadata.get('transform')
        
        results = []
        for change in changes:
            pixel_col = change['centroid'][0] + col_off
            pixel_row = change['centroid'][1] + row_off
            
            lng, lat = self.pixel_to_coordinates(pixel_col, pixel_row, transform)
            
            results.append({
                'location': {'lng': lng, 'lat': lat},
                'pixel_location': {'col': pixel_col, 'row': pixel_row},
                'change_type': change['change_type'],
                'change_percentage': abs(change['mean_change']) * 100,
                'pixel_count': change['pixel_count'],
                'severity': change['severity'],
            })
        
        return {
            'window': window,
            'detections': results,
        }
    
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge change detection results from all chunks.
        """
        all_detections = []
        
        for result in chunk_results:
            if result and 'detections' in result:
                all_detections.extend(result['detections'])
        
        # Group by change type
        by_type = {}
        for detection in all_detections:
            change_type = detection['change_type']
            if change_type not in by_type:
                by_type[change_type] = []
            by_type[change_type].append(detection)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_detections.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        summary = self._generate_summary(all_detections, by_type)
        
        return {
            'analysis_type': 'change',
            'detections': all_detections,
            'by_type': by_type,
            'summary': summary,
            'total_changes': len(all_detections),
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
        Generate human-readable summary of change detection.
        """
        if not detections:
            return (
                "No significant changes were detected in the monitored area. "
                "The landscape appears stable compared to the baseline."
            )
        
        type_descriptions = {
            'vegetation_loss': 'areas of vegetation loss',
            'vegetation_gain': 'areas of new vegetation growth',
            'construction': 'new construction or development',
            'erosion': 'erosion or land degradation',
            'unknown': 'unclassified changes',
        }
        
        parts = [f"Analysis detected {len(detections)} significant change(s) in the area."]
        
        for change_type, items in by_type.items():
            if items:
                desc = type_descriptions.get(change_type, change_type)
                parts.append(f"Found {len(items)} {desc}.")
        
        critical = len([d for d in detections if d['severity'] == 'critical'])
        if critical > 0:
            parts.append(
                f"ATTENTION: {critical} change(s) classified as critical "
                f"require immediate investigation."
            )
        
        parts.append(
            "Review the detected changes on the map and investigate "
            "any that may affect pipeline integrity or safety."
        )
        
        return " ".join(parts)

