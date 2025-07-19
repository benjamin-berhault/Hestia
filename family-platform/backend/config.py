from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://family_user:family_pass@localhost:5432/family_db"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "family-platform"
    minio_secure: bool = False
    
    # Email
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@familyplatform.com"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    
    # Application
    app_name: str = "Family-Centered Relationship Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    allowed_hosts: list = ["*"]
    
    # Security
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: list = ["image/jpeg", "image/png", "image/webp"]
    
    # Redis (for caching and sessions)
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

settings = Settings()