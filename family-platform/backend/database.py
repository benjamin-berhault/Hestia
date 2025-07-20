from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from config import settings
import logging
import structlog
from typing import Generator

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create SQLAlchemy engine with advanced configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.debug,
    "pool_size": settings.database_pool_size,
    "max_overflow": settings.database_max_overflow,
    "pool_timeout": settings.database_pool_timeout,
    "pool_recycle": 3600,  # Recycle connections every hour
}

# Use QueuePool for PostgreSQL, StaticPool for SQLite
if "postgresql" in settings.database_url:
    engine_kwargs["poolclass"] = QueuePool
elif "sqlite" in settings.database_url:
    engine_kwargs["poolclass"] = StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)

# Add connection event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance"""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log database connection checkout"""
    logger.debug("Database connection checked out", 
                connection_id=id(dbapi_connection))

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log database connection checkin"""
    logger.debug("Database connection checked in", 
                connection_id=id(dbapi_connection))

# Create SessionLocal class with advanced configuration
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Keep objects accessible after commit
)

# Create Base class for models
Base = declarative_base()

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        """Dependency to get database session with proper error handling"""
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error("Database session error", error=str(e), exc_info=True)
            db.rollback()
            raise
        finally:
            db.close()
    
    @staticmethod
    def create_tables():
        """Create all tables with error handling"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating tables", error=str(e), exc_info=True)
            raise
    
    @staticmethod
    def drop_tables():
        """Drop all tables (for testing)"""
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error("Error dropping tables", error=str(e), exc_info=True)
            raise
    
    @staticmethod
    def get_engine_stats():
        """Get database engine statistics"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
            "invalid_connections": pool.invalid(),
        }
    
    @staticmethod
    def health_check() -> bool:
        """Check database health"""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
get_db = db_manager.get_db
create_tables = db_manager.create_tables
drop_tables = db_manager.drop_tables