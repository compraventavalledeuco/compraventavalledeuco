#!/usr/bin/env python3
"""
Cloudinary Storage Integration - Free Alternative to AWS S3
Handles image uploads with automatic optimization and CDN
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime
import uuid
import logging
from werkzeug.utils import secure_filename

class CloudinaryStorage:
    def __init__(self):
        """Initialize Cloudinary with environment variables"""
        self.cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        self.api_key = os.environ.get('CLOUDINARY_API_KEY')
        self.api_secret = os.environ.get('CLOUDINARY_API_SECRET')
        
        if self.cloud_name and self.api_key and self.api_secret:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=True
            )
            self.enabled = True
        else:
            self.enabled = False
            logging.warning("Cloudinary credentials not configured. Using local storage.")
    
    def upload_file(self, file, folder='vehicle_images'):
        """
        Upload file to Cloudinary
        Returns: dict with success status and file URL or error
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Cloudinary not configured'
            }
        
        try:
            # Generate unique public_id
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = secure_filename(file.filename)
            name_without_ext = os.path.splitext(filename)[0]
            public_id = f"{folder}/{timestamp}_{unique_id}_{name_without_ext}"
            
            # Upload to Cloudinary with optimizations
            result = cloudinary.uploader.upload(
                file,
                public_id=public_id,
                folder=folder,
                resource_type="auto",
                # Automatic optimizations
                quality="auto:good",
                fetch_format="auto",
                # Generate different sizes
                eager=[
                    {"width": 800, "height": 600, "crop": "fill", "quality": "auto:good"},
                    {"width": 400, "height": 300, "crop": "fill", "quality": "auto:good"},
                    {"width": 150, "height": 150, "crop": "fill", "quality": "auto:good"}
                ]
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'filename': filename,
                'thumbnails': {
                    'large': result['eager'][0]['secure_url'] if result.get('eager') else result['secure_url'],
                    'medium': result['eager'][1]['secure_url'] if len(result.get('eager', [])) > 1 else result['secure_url'],
                    'small': result['eager'][2]['secure_url'] if len(result.get('eager', [])) > 2 else result['secure_url']
                }
            }
            
        except Exception as e:
            logging.error(f"Cloudinary upload error: {e}")
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def delete_file(self, public_id):
        """Delete file from Cloudinary"""
        if not self.enabled:
            return False
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            logging.error(f"Cloudinary delete error: {e}")
            return False
    
    def list_files(self, folder='vehicle_images', max_results=100):
        """List files in Cloudinary folder"""
        if not self.enabled:
            return []
        
        try:
            result = cloudinary.api.resources(
                type="upload",
                prefix=f"{folder}/",
                max_results=max_results
            )
            
            files = []
            for resource in result.get('resources', []):
                files.append({
                    'public_id': resource['public_id'],
                    'url': resource['secure_url'],
                    'size': resource['bytes'],
                    'created_at': resource['created_at'],
                    'format': resource['format']
                })
            
            return files
        except Exception as e:
            logging.error(f"Cloudinary list error: {e}")
            return []
    
    def get_optimized_url(self, public_id, width=None, height=None, quality="auto:good"):
        """Get optimized URL for existing image"""
        if not self.enabled:
            return None
        
        try:
            transformations = {
                'quality': quality,
                'fetch_format': 'auto'
            }
            
            if width and height:
                transformations.update({
                    'width': width,
                    'height': height,
                    'crop': 'fill'
                })
            
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformations)
            return url
        except Exception as e:
            logging.error(f"Cloudinary URL generation error: {e}")
            return None

# Global instance
cloudinary_storage = CloudinaryStorage()

def upload_to_cloudinary(file, folder='vehicle_images'):
    """Convenience function for uploading files"""
    return cloudinary_storage.upload_file(file, folder)

def delete_from_cloudinary(public_id):
    """Convenience function for deleting files"""
    return cloudinary_storage.delete_file(public_id)
