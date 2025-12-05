"""
NDVI-based leak detection processor.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

from .base import BaseProcessor

logger = logging.getLogger('analysis')


class NDVIProcessor(BaseProcessor):
    """
    Processor for NDVI-based leak detection.
    
    Uses Normalized Difference Vegetation Index to detect potential
    oil spills and leaks by identifying areas of stressed or dead vegetation.
    """
    
    # NDVI thresholds for anomaly detection
    NDVI_HEALTHY_MIN = 0.3  # Healthy vegetation
    NDVI_STRESSED_MIN = 0.1  # Stressed vegetation
    NDVI_ANOMALY_MAX = 0.1  # Potential leak indicator
    
    # Severity thresholds based on NDVI drop
    SEVERITY_THRESHOLDS = {
        'critical': 0.9,
        'high': 0.7,
        'medium': 0.5,
        'low': 0.3,
    }
    
    def __init__(
        self,
        nir_band: int = 4,
        red_band: int = 3,
        **kwargs
    ):
        """
        Initialize NDVI processor.
        
        Args:
            nir_band: Band index for Near-Infrared (1-indexed)
            red_band: Band index for Red band (1-indexed)
        """
        super().__init__(**kwargs)
        self.nir_band = nir_band - 1  # Convert to 0-indexed
        self.red_band = red_band - 1
    
    def calculate_ndvi(self, data: np.ndarray) -> np.ndarray:
        """
        Calculate NDVI from image bands.
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            data: Image data array (bands, height, width)
            
        Returns:
            NDVI array
        """
        if data.shape[0] < max(self.nir_band, self.red_band) + 1:
            logger.warning(
                f"Image has {data.shape[0]} bands, "
                f"but NIR={self.nir_band + 1} and Red={self.red_band + 1} requested"
            )
            return None
        
        nir = data[self.nir_band].astype(np.float32)
        red = data[self.red_band].astype(np.float32)
        
        # Avoid division by zero
        denominator = nir + red
        denominator[denominator == 0] = 1
        
        ndvi = (nir - red) / denominator
        
        # Clip to valid NDVI range
        ndvi = np.clip(ndvi, -1, 1)
        
        return ndvi
    
    def detect_anomalies(
        self,
        ndvi: np.ndarray,
        threshold: float = None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect anomalies in NDVI data.
        
        Args:
            ndvi: NDVI array
            threshold: Threshold for anomaly detection
            
        Returns:
            Tuple of (anomaly mask, list of anomaly regions)
        """
        threshold = threshold or self.NDVI_ANOMALY_MAX
        
        # Create anomaly mask
        anomaly_mask = ndvi < threshold
        
        # Find connected regions
        try:
            from scipy import ndimage
            labeled, num_features = ndimage.label(anomaly_mask)
            regions = []
            
            for i in range(1, num_features + 1):
                region_mask = labeled == i
                region_pixels = np.sum(region_mask)
                
                # Skip very small regions (noise)
                if region_pixels < 10:
                    continue
                
                # Calculate region statistics
                region_ndvi = ndvi[region_mask]
                mean_ndvi = float(np.mean(region_ndvi))
                min_ndvi = float(np.min(region_ndvi))
                
                # Find centroid
                coords = np.where(region_mask)
                centroid_row = int(np.mean(coords[0]))
                centroid_col = int(np.mean(coords[1]))
                
                # Calculate severity
                ndvi_drop = abs(min_ndvi)
                severity = self.get_severity(ndvi_drop, self.SEVERITY_THRESHOLDS)
                
                regions.append({
                    'centroid': (centroid_col, centroid_row),
                    'pixel_count': int(region_pixels),
                    'mean_ndvi': mean_ndvi,
                    'min_ndvi': min_ndvi,
                    'severity': severity,
                })
            
            return anomaly_mask, regions
            
        except ImportError:
            logger.warning("scipy not available for region analysis")
            return anomaly_mask, []
    
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a chunk for NDVI analysis.
        """
        col_off, row_off, win_width, win_height = window
        
        # Calculate NDVI
        ndvi = self.calculate_ndvi(data)
        if ndvi is None:
            return None
        
        # Detect anomalies
        _, anomalies = self.detect_anomalies(ndvi)
        
        if not anomalies:
            return None
        
        # Convert pixel coordinates to geographic coordinates
        transform = metadata.get('transform')
        
        results = []
        for anomaly in anomalies:
            # Adjust coordinates for window offset
            pixel_col = anomaly['centroid'][0] + col_off
            pixel_row = anomaly['centroid'][1] + row_off
            
            # Convert to geographic coordinates
            lng, lat = self.pixel_to_coordinates(pixel_col, pixel_row, transform)
            
            results.append({
                'location': {'lng': lng, 'lat': lat},
                'pixel_location': {'col': pixel_col, 'row': pixel_row},
                'ndvi_value': anomaly['mean_ndvi'],
                'pixel_count': anomaly['pixel_count'],
                'severity': anomaly['severity'],
            })
        
        return {
            'window': window,
            'detections': results,
            'statistics': {
                'mean_ndvi': float(np.nanmean(ndvi)),
                'min_ndvi': float(np.nanmin(ndvi)),
                'max_ndvi': float(np.nanmax(ndvi)),
            }
        }
    
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge NDVI analysis results from all chunks.
        """
        all_detections = []
        all_stats = []
        
        for result in chunk_results:
            if result and 'detections' in result:
                all_detections.extend(result['detections'])
            if result and 'statistics' in result:
                all_stats.append(result['statistics'])
        
        # Calculate overall statistics
        overall_stats = {}
        if all_stats:
            overall_stats = {
                'mean_ndvi': np.mean([s['mean_ndvi'] for s in all_stats]),
                'min_ndvi': min([s['min_ndvi'] for s in all_stats]),
                'max_ndvi': max([s['max_ndvi'] for s in all_stats]),
            }
        
        # Sort detections by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_detections.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        # Generate summary
        summary = self._generate_summary(all_detections, overall_stats)
        
        return {
            'analysis_type': 'ndvi',
            'detections': all_detections,
            'statistics': overall_stats,
            'summary': summary,
            'total_anomalies': len(all_detections),
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
        statistics: Dict
    ) -> str:
        """
        Generate human-readable summary of NDVI analysis.
        """
        if not detections:
            return (
                "No potential leaks or oil spills were detected in this image. "
                "The vegetation health across the analyzed area appears normal "
                "with no signs of hydrocarbon contamination."
            )
        
        critical = len([d for d in detections if d['severity'] == 'critical'])
        high = len([d for d in detections if d['severity'] == 'high'])
        
        summary_parts = [
            f"Analysis detected {len(detections)} area(s) of concern "
            f"that may indicate potential oil spills or leaks."
        ]
        
        if critical > 0:
            summary_parts.append(
                f"URGENT: {critical} critical area(s) detected with severely "
                f"stressed or dead vegetation, strongly suggesting active contamination."
            )
        
        if high > 0:
            summary_parts.append(
                f"{high} high-severity area(s) show significant vegetation stress "
                f"that warrants immediate investigation."
            )
        
        if statistics:
            mean_ndvi = statistics.get('mean_ndvi', 0)
            if mean_ndvi < 0.2:
                summary_parts.append(
                    "Overall vegetation health in the area is poor, "
                    "indicating widespread environmental stress."
                )
        
        summary_parts.append(
            "Recommended action: Deploy field teams to inspect flagged locations "
            "and verify potential contamination."
        )
        
        return " ".join(summary_parts)

