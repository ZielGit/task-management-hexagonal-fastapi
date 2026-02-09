from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base para todos los modelos SQLAlchemy"""
    pass


class TaskModel(Base):
    """
    Modelo de base de datos para Task.
    Representa la estructura de la tabla en PostgreSQL.
    """
    __tablename__ = "tasks"
    
    # Columnas
    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )
    
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=""
    )
    
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="medium"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="todo"
    )
    
    assigned_to: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<TaskModel(id={self.id}, title='{self.title}', status='{self.status}')>"


class UserModel(Base):
    """
    Modelo de base de datos para User.
    Representa la estructura de la tabla en PostgreSQL.
    """
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )
    
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"
