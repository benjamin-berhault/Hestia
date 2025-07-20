from minio import Minio
from minio.error import S3Error
from config import settings
import logging
from typing import Optional, IO
import uuid
from PIL import Image
import io

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def upload_image(self, file_data: bytes, content_type: str, user_id: int, folder: str = "profiles") -> str:
        """Upload image file and return the object name"""
        try:
            # Validate content type
            if content_type not in settings.allowed_image_types:
                raise ValueError(f"Invalid image type: {content_type}")
            
            # Generate unique filename
            file_extension = content_type.split('/')[-1]
            object_name = f"{folder}/{user_id}/{uuid.uuid4()}.{file_extension}"
            
            # Optimize image
            optimized_data = self._optimize_image(file_data, content_type)
            
            # Upload to MinIO
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(optimized_data),
                length=len(optimized_data),
                content_type=content_type
            )
            
            logger.info(f"Uploaded image: {object_name}")
            return object_name
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise
    
    def _optimize_image(self, file_data: bytes, content_type: str, max_size: tuple = (800, 800), quality: int = 85) -> bytes:
        """Optimize image for web usage"""
        try:
            # Open image
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output_buffer = io.BytesIO()
            format_mapping = {
                'image/jpeg': 'JPEG',
                'image/png': 'PNG',
                'image/webp': 'WEBP'
            }
            
            image_format = format_mapping.get(content_type, 'JPEG')
            save_kwargs = {'format': image_format, 'optimize': True}
            
            if image_format == 'JPEG':
                save_kwargs['quality'] = quality
            
            image.save(output_buffer, **save_kwargs)
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            # Return original if optimization fails
            return file_data
    
    def get_presigned_url(self, object_name: str, expires_in_hours: int = 24) -> str:
        """Get presigned URL for accessing an object"""
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(hours=expires_in_hours)
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def delete_object(self, object_name: str) -> bool:
        """Delete an object from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted object: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting object: {e}")
            return False
    
    def list_user_objects(self, user_id: int, folder: str = "profiles") -> list:
        """List all objects for a user"""
        try:
            prefix = f"{folder}/{user_id}/"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing objects: {e}")
            return []

# Global MinIO client instance
minio_client = MinIOClient()