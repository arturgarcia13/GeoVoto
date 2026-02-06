from typing import Generator
import logging

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from geovoto.config.settings import settings

logger = logging.getLogger(__name__)

# Global engine instance
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Creates or returns the global SQLAlchemy engine.
    This function is cached by Streamlit in the UI layer, 
    but here it returns a standard engine based on settings.
    """
    global _engine
    
    if _engine is None:
        logger.info(f"Connecting to database at {settings.database.host}...")
        try:
            _engine = create_engine(
                settings.database.connection_string,
                pool_size=settings.database.pool_size,
                pool_timeout=settings.database.pool_timeout,
                pool_pre_ping=True
            )
        except Exception as e:
            logger.critical(f"Failed to create database engine: {e}")
            raise e
            
    return _engine


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
