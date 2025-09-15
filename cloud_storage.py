#!/usr/bin/env python3
"""
Cloud Storage Integration for Heroku
Handles image uploads to AWS S3 for persistent storage
"""

import os
import boto3
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import logging

class CloudStorage:
    def __init__(self):
        """Initialize S3 client with environment variables"""
        self.s3_bucket = os.environ.get('S3_BUCKET_NAME')
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        if self.s3_bucket and self.aws_access_key and self.aws_secret_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                self.enabled = True
            except Exception as e:
                logging.error(f"Error initializing S3 client: {e}")
                self.enabled = False
        else:
            self.enabled = False
            logging.warning("S3 credentials not configured. Using local storage.")
    
    def upload_file(self, file, folder='uploads'):
        """
        Upload file to S3 bucket
        Returns: dict with success status and file URL or error
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Cloud storage not configured'
            }
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = secure_filename(file.filename)
            s3_key = f"{folder}/{timestamp}_{unique_id}_{filename}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type or 'application/octet-stream',
                    'ACL': 'public-read'  # Make files publicly accessible
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            return {
                'success': True,
                'url': file_url,
                's3_key': s3_key,
                'filename': filename
            }
            
        except ClientError as e:
            logging.error(f"S3 upload error: {e}")
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
        except Exception as e:
            logging.error(f"Unexpected upload error: {e}")
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def delete_file(self, s3_key):
        """Delete file from S3 bucket"""
        if not self.enabled:
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except Exception as e:
            logging.error(f"S3 delete error: {e}")
            return False
    
    def list_files(self, folder='uploads'):
        """List files in S3 bucket folder"""
        if not self.enabled:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=f"{folder}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{obj['Key']}"
                })
            
            return files
        except Exception as e:
            logging.error(f"S3 list error: {e}")
            return []
    
    def get_file_url(self, s3_key):
        """Get public URL for S3 file"""
        if not self.enabled:
            return None
        
        return f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}"

# Global instance
cloud_storage = CloudStorage()

def upload_to_cloud(file, folder='uploads'):
    """Convenience function for uploading files"""
    return cloud_storage.upload_file(file, folder)

def delete_from_cloud(s3_key):
    """Convenience function for deleting files"""
    return cloud_storage.delete_file(s3_key)
