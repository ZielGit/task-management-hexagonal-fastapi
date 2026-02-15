from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .sqlalchemy_task_repository import SQLAlchemyTaskRepository
from .sqlalchemy_user_repository import SQLAlchemyUserRepository


class UnitOfWork:
    """
    Implementación del patrón Unit of Work con SQLAlchemy.

    Agrupa los repositorios bajo una misma sesión/transacción,
    exponiendo commit() y rollback() para controlar el ciclo
    de vida de forma explícita.

    Uso como context manager (recomendado):
        async with UnitOfWork(session) as uow:
            user = await uow.users.save(user)
            task = await uow.tasks.save(task)
            # commit automático al salir sin excepciones

    Uso manual:
        uow = UnitOfWork(session)
        await uow.begin()
        try:
            await uow.users.save(user)
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
    """

    def __init__(self, session: AsyncSession):
        """
        Args:
            session: Sesión de SQLAlchemy compartida por todos los repositorios.
        """
        self._session = session
        self._tasks: Optional[SQLAlchemyTaskRepository] = None
        self._users: Optional[SQLAlchemyUserRepository] = None

    # ============= REPOSITORIOS (lazy init) =============

    @property
    def tasks(self) -> SQLAlchemyTaskRepository:
        """Repositorio de tareas ligado a la sesión actual."""
        if self._tasks is None:
            self._tasks = SQLAlchemyTaskRepository(self._session)
        return self._tasks

    @property
    def users(self) -> SQLAlchemyUserRepository:
        """Repositorio de usuarios ligado a la sesión actual."""
        if self._users is None:
            self._users = SQLAlchemyUserRepository(self._session)
        return self._users

    # ============= CICLO DE VIDA DE LA TRANSACCIÓN =============

    async def commit(self) -> None:
        """
        Confirma todos los cambios pendientes en la base de datos.

        Raises:
            Exception: Si el commit falla, realiza rollback automático.
        """
        try:
            await self._session.commit()
        except Exception:
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """Revierte todos los cambios no confirmados."""
        await self._session.rollback()

    async def flush(self) -> None:
        """
        Envía los cambios pendientes a la BD sin confirmarlos.
        Útil para obtener IDs generados antes del commit final.
        """
        await self._session.flush()

    # ============= CONTEXT MANAGER =============

    async def __aenter__(self) -> "UnitOfWork":
        """Inicia el contexto del Unit of Work."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Cierra el contexto:
        - Sin excepción → commit automático.
        - Con excepción → rollback automático.
        """
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
