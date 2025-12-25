"""Database configuration and connection setup."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://charlee:charlee123@localhost:5432/charlee_db"

    # Database connection pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600  # Recycle connections after 1 hour

    # Authentication & JWT
    jwt_secret_key: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    jwt_refresh_secret_key: str = "your-refresh-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Anthropic API
    anthropic_api_key: str = ""

    # Application
    app_env: str = "development"
    debug: bool = True

    # Calendar Integration
    google_calendar_redirect_uri: str = "http://localhost:3000/calendar/callback/google"
    microsoft_calendar_redirect_uri: str = "http://localhost:3000/calendar/callback/microsoft"

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
