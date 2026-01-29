from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    Lee variables de entorno y archivo .env
    """
    
    # ============= DATABASE =============
    POSTGRES_USER: str = Field(default="taskuser")
    POSTGRES_PASSWORD: str = Field(default="taskpass")
    POSTGRES_DB: str = Field(default="taskdb")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskdb"
    )
    
    # Database pool configuration
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=3600)
    
    # ============= API =============
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    
    # ============= JWT =============
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-key-change-this-in-production"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_MINUTES: int = Field(default=1440)  # 24 hours
    
    # ============= CORS =============
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS
    
    # ============= LOGGING =============
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")  # json | text
    
    # ============= PAGINATION =============
    DEFAULT_PAGE_SIZE: int = Field(default=100)
    MAX_PAGE_SIZE: int = Field(default=1000)
    
    # ============= RATE LIMITING =============
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)
    
    # ============= FEATURE FLAGS =============
    ENABLE_DOCS: bool = Field(default=True)
    ENABLE_METRICS: bool = Field(default=True)
    
    # Configuración del modelo Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ============= COMPUTED PROPERTIES =============
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic"""
        return self.DATABASE_URL.replace("+asyncpg", "")
    
    def get_database_url(self) -> str:
        """
        Construye la URL de base de datos desde componentes individuales.
        Útil si DATABASE_URL no está definida directamente.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para obtener settings.
    Usa LRU cache para evitar recrear el objeto en cada llamada.
    
    Returns:
        Instancia única de Settings
    """
    return Settings()


# Exportar para facilitar imports
settings = get_settings()
