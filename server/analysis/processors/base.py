"""
Base processor for image analysis with windowed/chunked processing.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Generator, Tuple, Optional, Dict, List
import numpy as np
from django.conf import settings

logger = logging.getLogger('analysis')


class BaseProcessor(ABC):
    """
    Base class for image processors with chunked/windowed processing support.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        overlap: int = None,
        progress_callback: Optional[callable] = None
    ):
        """
        Initialize the processor.
        
        Args:
            chunk_size: Size of each processing chunk (default from settings)
            overlap: Overlap between chunks to avoid edge artifacts
            progress_callback: Optional callback for progress updates
        """
        self.chunk_size = chunk_size or getattr(settings, 'ANALYSIS_CHUNK_SIZE', 1024)
        self.overlap = overlap or getattr(settings, 'ANALYSIS_OVERLAP', 64)
        self.progress_callback = progress_callback
        
    def get_windows(
        self,
        width: int,
        height: int
    ) -> Generator[Tuple[int, int, int, int], None, None]:
        """
        Generate window coordinates for chunked processing.
        
        Args:
            width: Image width
            height: Image height
            
        Yields:
            Tuple of (col_off, row_off, win_width, win_height)
        """
        step = self.chunk_size - self.overlap
        
        for row_off in range(0, height, step):
            for col_off in range(0, width, step):
                # Calculate window dimensions
                win_width = min(self.chunk_size, width - col_off)
                win_height = min(self.chunk_size, height - row_off)
                
                yield (col_off, row_off, win_width, win_height)
    
    def count_windows(self, width: int, height: int) -> int:
        """
        Count total number of windows for an image.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Total number of windows
        """
        step = self.chunk_size - self.overlap
        cols = (width + step - 1) // step
        rows = (height + step - 1) // step
        return cols * rows
    
    def update_progress(
        self,
        current: int,
        total: int,
        message: str = ""
    ) -> None:
        """
        Update processing progress.
        
        Args:
            current: Current step
            total: Total steps
            message: Optional progress message
        """
        if self.progress_callback:
            progress = int((current / total) * 100) if total > 0 else 0
            self.progress_callback(progress, message)
    
    @abstractmethod
    def process_chunk(
        self,
        data: np.ndarray,
        window: Tuple[int, int, int, int],
        metadata: Dict
    ) -> Dict:
        """
        Process a single chunk of the image.
        
        Args:
            data: Numpy array of chunk data
            window: Window coordinates (col_off, row_off, width, height)
            metadata: Image metadata including transform, CRS, etc.
            
        Returns:
            Dict containing analysis results for the chunk
        """
        pass
    
    @abstractmethod
    def merge_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Merge results from all chunks into final result.
        
        Args:
            chunk_results: List of results from each chunk
            
        Returns:
            Merged analysis results
        """
        pass
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process an entire image using windowed/chunked approach.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Complete analysis results
        """
        try:
            import rasterio
            from rasterio.windows import Window
        except ImportError:
            logger.error("rasterio not available")
            return {'error': 'rasterio not installed'}
        
        if not os.path.exists(image_path):
            return {'error': f'Image file not found: {image_path}'}
        
        chunk_results = []
        
        try:
            with rasterio.open(image_path) as src:
                width = src.width
                height = src.height
                total_windows = self.count_windows(width, height)
                
                metadata = {
                    'crs': str(src.crs) if src.crs else None,
                    'transform': src.transform,
                    'bounds': src.bounds,
                    'width': width,
                    'height': height,
                    'count': src.count,
                    'dtype': str(src.dtypes[0]),
                }
                
                logger.info(
                    f"Processing image {image_path}: "
                    f"{width}x{height}, {total_windows} chunks"
                )
                
                for idx, (col_off, row_off, win_width, win_height) in enumerate(
                    self.get_windows(width, height)
                ):
                    window = Window(col_off, row_off, win_width, win_height)
                    
                    # Read chunk data
                    data = src.read(window=window)
                    
                    # Process chunk
                    result = self.process_chunk(
                        data,
                        (col_off, row_off, win_width, win_height),
                        metadata
                    )
                    
                    if result:
                        chunk_results.append(result)
                    
                    # Update progress
                    self.update_progress(
                        idx + 1,
                        total_windows,
                        f"Processing chunk {idx + 1}/{total_windows}"
                    )
                
                # Merge results
                final_result = self.merge_results(chunk_results)
                final_result['metadata'] = metadata
                final_result['chunks_processed'] = len(chunk_results)
                
                return final_result
                
        except Exception as e:
            logger.exception(f"Error processing image: {e}")
            return {'error': str(e)}
    
    def pixel_to_coordinates(
        self,
        col: int,
        row: int,
        transform
    ) -> Tuple[float, float]:
        """
        Convert pixel coordinates to geographic coordinates.
        
        Args:
            col: Column (x) pixel coordinate
            row: Row (y) pixel coordinate
            transform: Rasterio transform
            
        Returns:
            Tuple of (longitude, latitude)
        """
        if transform is None:
            return (col, row)
        
        x, y = transform * (col, row)
        return (x, y)
    
    def get_severity(self, value: float, thresholds: Dict[str, float]) -> str:
        """
        Determine severity based on value and thresholds.
        
        Args:
            value: Value to evaluate
            thresholds: Dict with 'critical', 'high', 'medium', 'low' thresholds
            
        Returns:
            Severity string
        """
        if value >= thresholds.get('critical', 0.9):
            return 'critical'
        elif value >= thresholds.get('high', 0.7):
            return 'high'
        elif value >= thresholds.get('medium', 0.5):
            return 'medium'
        else:
            return 'low'

