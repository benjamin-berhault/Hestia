from sqlalchemy import Column, Integer, DateTime, Boolean, Float, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from typing import Optional

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False)
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Mark record as deleted without removing from database"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None

class AuditMixin(TimestampMixin):
    """Mixin for audit trail functionality"""
    
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, nullable=True)

class GeoLocationMixin:
    """Mixin for geolocation data"""
    
    @declared_attr
    def latitude(cls):
        return Column(Float, nullable=True)
    
    @declared_attr
    def longitude(cls):
        return Column(Float, nullable=True)
    
    @declared_attr
    def city(cls):
        return Column(String(100), nullable=True)
    
    @declared_attr
    def state(cls):
        return Column(String(50), nullable=True)
    
    @declared_attr
    def country(cls):
        return Column(String(50), nullable=True)
    
    @declared_attr
    def postal_code(cls):
        return Column(String(20), nullable=True)