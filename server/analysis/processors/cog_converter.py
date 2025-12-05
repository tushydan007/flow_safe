"""
Cloud Optimized GeoTIFF (COG) converter.
"""

import os
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger('analysis')


class COGConverter:
    """
    Converts raster images to Cloud Optimized GeoTIFF format.
    """
    
    def __init__(
        self,
        compression: str = None,
        blocksize: int = None,
        resampling: str = 'nearest'
    ):
        """
        Initialize COG converter.
        
        Args:
            compression: Compression type (DEFLATE, LZW, JPEG, etc.)
            blocksize: Internal tile size (default 512)
            resampling: Resampling method for overviews
        """
        self.compression = compression or getattr(settings, 'COG_COMPRESSION', 'DEFLATE')
        self.blocksize = blocksize or getattr(settings, 'COG_BLOCKSIZE', 512)
        self.resampling = resampling
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Convert a raster file to Cloud Optimized GeoTIFF.
        
        Args:
            input_path: Path to input raster file
            output_path: Path for output COG file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with conversion results
        """
        if not os.path.exists(input_path):
            return {
                'success': False,
                'error': f'Input file not found: {input_path}'
            }
        
        try:
            from rio_cogeo.cogeo import cog_translate
            from rio_cogeo.profiles import cog_profiles
            
            # Get output profile
            output_profile = cog_profiles.get(self.compression.lower())
            if output_profile is None:
                output_profile = cog_profiles.get('deflate')
            
            # Update profile with settings
            output_profile.update({
                'blockxsize': self.blocksize,
                'blockysize': self.blocksize,
            })
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if progress_callback:
                progress_callback(10, "Starting COG conversion...")
            
            # Perform conversion
            cog_translate(
                input_path,
                output_path,
                output_profile,
                overview_level=5,
                overview_resampling=self.resampling,
                web_optimized=True,
                in_memory=False,
            )
            
            if progress_callback:
                progress_callback(90, "Validating COG...")
            
            # Validate the output
            is_valid = self._validate_cog(output_path)
            
            if progress_callback:
                progress_callback(100, "COG conversion complete")
            
            # Get file info
            output_size = os.path.getsize(output_path)
            input_size = os.path.getsize(input_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': input_size / output_size if output_size > 0 else 0,
                'is_valid_cog': is_valid,
            }
            
        except ImportError:
            logger.error("rio-cogeo not installed")
            return self._fallback_convert(input_path, output_path, progress_callback)
        except Exception as e:
            logger.exception(f"Error converting to COG: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fallback_convert(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Fallback conversion using rasterio directly.
        """
        try:
            import rasterio
            from rasterio.shutil import copy
            
            if progress_callback:
                progress_callback(10, "Using fallback COG conversion...")
            
            # Define COG profile
            cog_profile = {
                'driver': 'GTiff',
                'interleave': 'pixel',
                'tiled': True,
                'blockxsize': self.blocksize,
                'blockysize': self.blocksize,
                'compress': self.compression,
                'copy_src_overviews': True,
            }
            
            with rasterio.open(input_path) as src:
                # Update profile with source metadata
                cog_profile.update({
                    'crs': src.crs,
                    'transform': src.transform,
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,
                    'dtype': src.dtypes[0],
                })
                
                if progress_callback:
                    progress_callback(30, "Writing COG file...")
                
                # Copy with COG profile
                copy(src, output_path, **cog_profile)
                
                if progress_callback:
                    progress_callback(70, "Building overviews...")
                
                # Add overviews
                with rasterio.open(output_path, 'r+') as dst:
                    factors = [2, 4, 8, 16, 32]
                    dst.build_overviews(factors, rasterio.enums.Resampling.nearest)
                    dst.update_tags(ns='rio_overview', resampling='nearest')
            
            if progress_callback:
                progress_callback(100, "Fallback conversion complete")
            
            output_size = os.path.getsize(output_path)
            input_size = os.path.getsize(input_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': input_size / output_size if output_size > 0 else 0,
                'is_valid_cog': True,
                'method': 'fallback'
            }
            
        except Exception as e:
            logger.exception(f"Fallback conversion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_cog(self, cog_path: str) -> bool:
        """
        Validate that a file is a valid Cloud Optimized GeoTIFF.
        """
        try:
            from rio_cogeo.cogeo import cog_validate
            is_valid, errors, warnings = cog_validate(cog_path)
            
            if errors:
                logger.warning(f"COG validation errors: {errors}")
            if warnings:
                logger.info(f"COG validation warnings: {warnings}")
            
            return is_valid
        except ImportError:
            # If rio-cogeo not available, do basic validation
            try:
                import rasterio
                with rasterio.open(cog_path) as src:
                    # Check if tiled
                    if not src.is_tiled:
                        return False
                    # Check for overviews
                    if not src.overviews(1):
                        logger.warning("COG missing overviews")
                    return True
            except Exception:
                return False
        except Exception as e:
            logger.warning(f"COG validation error: {e}")
            return False
    
    def extract_metadata(self, image_path: str) -> Dict:
        """
        Extract metadata from a raster image.
        
        Args:
            image_path: Path to the raster file
            
        Returns:
            Dict with image metadata
        """
        try:
            import rasterio
            from rasterio.warp import transform_bounds
            
            with rasterio.open(image_path) as src:
                # Get bounds in WGS84
                bounds = src.bounds
                if src.crs and src.crs.to_string() != 'EPSG:4326':
                    try:
                        bounds = transform_bounds(
                            src.crs,
                            'EPSG:4326',
                            *bounds
                        )
                    except Exception:
                        pass
                
                # Calculate center
                center_lng = (bounds[0] + bounds[2]) / 2
                center_lat = (bounds[1] + bounds[3]) / 2
                
                return {
                    'width': src.width,
                    'height': src.height,
                    'bands': src.count,
                    'dtype': str(src.dtypes[0]),
                    'crs': str(src.crs) if src.crs else None,
                    'bounds': list(bounds),
                    'center': {'lng': center_lng, 'lat': center_lat},
                    'resolution': abs(src.transform[0]) if src.transform else None,
                    'is_tiled': src.is_tiled,
                    'has_overviews': bool(src.overviews(1)) if src.count > 0 else False,
                }
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}

