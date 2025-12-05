"""
Emissions tracking processor using anomaly detection.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

from .base import BaseProcessor

logger = logging.getLogger('analysis')


class EmissionProcessor(BaseProcessor):
    """
    Processor for emissions tracking using anomaly detection.
    
    Detects thermal anomalies, methane plumes, and other emission indicators.
    """
    
    # Thresholds for emission detection
    THERMAL_ANOMALY_THRESHOLD = 2.0  # Standard deviations
    SEVERITY_THRESHOLDS = {
        'critical': 4.0,
        'high': 3.0,
        'medium': 2.5,
        'low': 2.0,
    }
    
    def __init__(
        self,
        thermal_band: int = None,
        swir_band: int = None,
        **kwargs
    ):
        """
        Initialize emission processor.
        
        Args:
            thermal_band: Band index for thermal infrared
            swir_band: Band index for SWIR (methane detection)
        """
        super().__init__(**kwargs)
        self.thermal_band = thermal_band
        self.swir_band = swir_band
    
    def detect_thermal_anomalies(
        self,
        data: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect thermal anomalies in the image.
        
        Args:
            data: Image data array
            
        Returns:
            Tuple of (anomaly mask, list of anomalies)
        """
        # Use the appropriate band or average of bands
        if self.thermal_band is not None and data.shape[0] > self.thermal_band:
            thermal = data[self.thermal_band].astype(np.float32)
        else:
            # Use last band or average as proxy
            thermal = np.mean(data, axis=0).astype(np.float32)
        
        # Calculate local statistics
        try:
            from scipy.ndimage import uniform_filter
            local_mean = uniform_filter(thermal, size=50)
            local_var = uniform_filter(thermal ** 2, size=50) - local_mean ** 2
            local_std = np.sqrt(np.maximum(local_var, 1e-6))
        except ImportError:
            local_mean = np.mean(thermal)
            local_std = np.std(thermal)
        
        # Calculate z-scores
        z_scores = (thermal - local_mean) / np.maximum(local_std, 1e-6)
        
        # Detect anomalies
        anomaly_mask = z_scores > self.THERMAL_ANOMALY_THRESHOLD
        
        # Find connected regions
        anomalies = []
        try:
            from scipy import ndimage
            labeled, num_features = ndimage.label(anomaly_mask)
            
            for i in range(1, num_features + 1):
                region_mask = labeled == i
                region_pixels = np.sum(region_mask)
                
                if region_pixels < 5:  # Skip very small regions
                    continue
                
                # Calculate statistics
                region_z = z_scores[region_mask]
                max_z = float(np.max(region_z))
                mean_z = float(np.mean(region_z))
                
                # Get intensity
                region_thermal = thermal[region_mask]
                intensity = float(np.max(region_thermal))
                
                # Find centroid
                coords = np.where(region_mask)
                centroid_row = int(np.mean(coords[0]))
                centroid_col = int(np.mean(coords[1]))
                
                # Determine emission type
                emission_type = 'heat'
                if max_z > 4.0:
                    emission_type = 'methane'  # Simplified classification
                
                # Calculate severity
                severity = self.get_severity(max_z, self.SEVERITY_THRESHOLDS)
                
                anomalies.append({
                    'centroid': (centroid_col, centroid_row),
                    'pixel_count': int(region_pixels),
                    'z_score': max_z,
                    'mean_z_score': mean_z,
                    'intensity': intensity,
                    'emission_type': emission_type,
                    'severity': severity,
                })
                
        except ImportError:
            logger.warning("scipy not available for region analysis")
        
        return anomaly_mask, anomalies
    
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a chunk for emission detection.
        """
        col_off, row_off, win_width, win_height = window
        
        # Detect anomalies
        _, anomalies = self.detect_thermal_anomalies(data)
        
        if not anomalies:
            return None
        
        transform = metadata.get('transform')
        
        results = []
        for anomaly in anomalies:
            pixel_col = anomaly['centroid'][0] + col_off
            pixel_row = anomaly['centroid'][1] + row_off
            
            lng, lat = self.pixel_to_coordinates(pixel_col, pixel_row, transform)
            
            # Estimate volume (simplified)
            estimated_volume = anomaly['pixel_count'] * anomaly['intensity'] * 0.001
            
            results.append({
                'location': {'lng': lng, 'lat': lat},
                'pixel_location': {'col': pixel_col, 'row': pixel_row},
                'emission_type': anomaly['emission_type'],
                'intensity': anomaly['intensity'],
                'z_score': anomaly['z_score'],
                'estimated_volume': estimated_volume,
                'pixel_count': anomaly['pixel_count'],
                'severity': anomaly['severity'],
            })
        
        return {
            'window': window,
            'detections': results,
        }
    
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge emission detection results.
        """
        all_detections = []
        
        for result in chunk_results:
            if result and 'detections' in result:
                all_detections.extend(result['detections'])
        
        # Group by emission type
        by_type = {}
        for detection in all_detections:
            emission_type = detection['emission_type']
            if emission_type not in by_type:
                by_type[emission_type] = []
            by_type[emission_type].append(detection)
        
        # Sort by severity/intensity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_detections.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['intensity']))
        
        summary = self._generate_summary(all_detections, by_type)
        
        # Calculate total estimated emissions
        total_volume = sum(d.get('estimated_volume', 0) for d in all_detections)
        
        return {
            'analysis_type': 'emission',
            'detections': all_detections,
            'by_type': by_type,
            'summary': summary,
            'total_anomalies': len(all_detections),
            'total_estimated_volume': total_volume,
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
        Generate human-readable summary of emission detection.
        """
        if not detections:
            return (
                "No emission anomalies or thermal hotspots were detected. "
                "The area shows normal thermal signatures with no signs of "
                "gas leaks, flaring, or other emission events."
            )
        
        parts = [
            f"Detected {len(detections)} emission anomaly/anomalies "
            f"that may indicate gas leaks or thermal events."
        ]
        
        for emission_type, items in by_type.items():
            if items:
                type_names = {
                    'methane': 'potential methane emission(s)',
                    'heat': 'thermal hotspot(s)',
                    'smoke': 'smoke/particulate event(s)',
                }
                name = type_names.get(emission_type, f'{emission_type} event(s)')
                max_intensity = max(i['intensity'] for i in items)
                parts.append(
                    f"Found {len(items)} {name} with peak intensity of {max_intensity:.1f}."
                )
        
        critical = [d for d in detections if d['severity'] == 'critical']
        if critical:
            parts.append(
                f"ALERT: {len(critical)} critical emission event(s) detected "
                f"requiring immediate investigation. These may indicate active "
                f"gas leaks or equipment failures."
            )
        
        total_volume = sum(d.get('estimated_volume', 0) for d in detections)
        if total_volume > 0:
            parts.append(
                f"Estimated total emission rate: {total_volume:.2f} kg/day. "
                f"This is an approximation and field verification is recommended."
            )
        
        parts.append(
            "Dispatch inspection teams to verify emission sources and "
            "take corrective action as needed."
        )
        
        return " ".join(parts)

