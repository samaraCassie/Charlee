"""Database configuration and connection setup."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://charlee:charlee123@localhost:5432/charlee_db"

    # Database connection pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600  # Recycle connections after 1 hour

    # Anthropic API
    anthropic_api_key: str = ""

    # Application
    app_env: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


# Initialize settings
settings = Settings()

# Create SQLAlchemy engine with connection pooling
# SQLite doesn't support pooling parameters, so we handle it differently
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,  # Prevent stale connections
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.

    Usage in FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
