from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Application Info
    app_name: str = "Family-Centered Relationship Platform"
    app_version: str = "1.0.0"
    app_description: str = "Building meaningful relationships for family-focused adults"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://family_user:family_pass@localhost:5432/family_db"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    
    # JWT Authentication
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_reset_expire_hours: int = 1
    email_verification_expire_hours: int = 24
    
    # MinIO Object Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "family-platform"
    minio_secure: bool = False
    minio_region: str = "us-east-1"
    
    # Email Configuration
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@familyplatform.com"
    mail_from_name: str = "Family Platform"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    
    # SMS & Phone (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    phone_verification_enabled: bool = False
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Celery Background Tasks
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Security Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
    allowed_hosts: List[str] = ["*"]
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    max_photos_per_user: int = 10
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    
    # Matching Algorithm
    matching_batch_size: int = 100
    compatibility_threshold: float = 0.6
    max_daily_matches: int = 10
    premium_max_daily_matches: int = 50
    
    # Geolocation
    max_search_radius_miles: int = 500
    default_search_radius_miles: int = 50
    geoip_database_path: str = "/app/data/GeoLite2-City.mmdb"
    
    # Content Moderation
    auto_moderation_enabled: bool = True
    face_detection_enabled: bool = True
    inappropriate_content_threshold: float = 0.8
    manual_review_threshold: float = 0.6
    
    # Video Calling (Agora)
    agora_app_id: str = ""
    agora_app_certificate: str = ""
    video_call_max_duration_minutes: int = 60
    
    # Real-time Communication
    pusher_app_id: str = ""
    pusher_key: str = ""
    pusher_secret: str = ""
    pusher_cluster: str = "us2"
    
    # Monitoring & Analytics
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    analytics_enabled: bool = True
    
    # Payments (Stripe)
    stripe_publishable_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    premium_monthly_price: int = 2999  # $29.99 in cents
    premium_annual_price: int = 19999  # $199.99 in cents
    
    # AI & ML Features
    ai_matching_enabled: bool = True
    personality_analysis_enabled: bool = True
    compatibility_ml_model_path: str = "/app/models/compatibility_model.pkl"
    
    # Charter System
    charter_templates_enabled: bool = True
    digital_signatures_enabled: bool = True
    charter_export_formats: List[str] = ["pdf", "docx"]
    
    # Profile Requirements
    min_age: int = 18
    max_age: int = 65
    profile_completion_required: int = 80  # Percentage
    min_photos_required: int = 3
    bio_min_length: int = 100
    family_vision_min_length: int = 50
    
    # Messaging
    max_message_length: int = 2000
    file_sharing_enabled: bool = True
    voice_messages_enabled: bool = True
    message_encryption_enabled: bool = True
    
    # Safety Features
    background_check_integration: bool = False
    id_verification_required: bool = False
    manual_profile_approval: bool = True
    automated_safety_alerts: bool = True
    
    # Business Logic
    free_tier_message_limit: int = 10
    free_tier_match_limit: int = 5
    premium_features_enabled: bool = True
    referral_program_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: str = "/app/logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()