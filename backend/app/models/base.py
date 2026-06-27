"""
Base Model with common fields for all database models.
"""
from datetime import datetime
from app.extensions import db


class BaseModel(db.Model):
    """Abstract base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Soft delete the record"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def save(self):
        """Save the record to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Hard delete the record"""
        db.session.delete(self)
        db.session.commit()


class TimestampMixin:
    """Mixin for adding timestamp fields to any model"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)