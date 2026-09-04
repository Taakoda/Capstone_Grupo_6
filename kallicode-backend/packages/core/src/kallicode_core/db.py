"""Acceso a PostgreSQL con multi-tenencia RLS (§3.3 del diseño).

Los .sql de db/ son la fuente de verdad del esquema (D06): este módulo NO
define modelos declarativos — trabaja con SQL parametrizado vía SQLAlchemy
Core (text()), que mantiene el código honesto respecto del DDL real.

Cada transacción de negocio abre sesión con el tenant fijado:

    async with sesion_tenant(tenant_id) as db:
        await db.execute(text("..."), {...})

`SET LOCAL app.tenant_id` activa las políticas RLS: la sesión queda confinada
al tenant y un recurso ajeno es indistinguible de uno inexistente (404).
Para operaciones de sistema (webhooks antes de resolver tenant, workers
multi-tenant) se usa `sesion_sistema()` con el usuario admin (BYPASSRLS).
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings

_engine_app = None
_sessionmaker_app: async_sessionmaker[AsyncSession] | None = None

_engine_admin = None
_sessionmaker_admin: async_sessionmaker[AsyncSession] | None = None


def engine_app_instancia():
    global _engine_app, _sessionmaker_app
    if _engine_app is None:
        s = get_settings()
        _engine_app = create_async_engine(s.database_url, pool_size=10, max_overflow=20,
                                         pool_pre_ping=True)
        _sessionmaker_app = async_sessionmaker(_engine_app, expire_on_commit=False)
    return _engine_app


def _maker_app() -> async_sessionmaker[AsyncSession]:
    engine_app_instancia()
    assert _sessionmaker_app is not None
    return _sessionmaker_app


def engine_admin_instancia():
    global _engine_admin, _sessionmaker_admin
    if _engine_admin is None:
        s = get_settings()
        # Si database_url_admin no está configurada, usa la principal por defecto
        url_admin = s.database_url_admin or s.database_url
        _engine_admin = create_async_engine(url_admin, pool_size=5, max_overflow=10,
                                          pool_pre_ping=True)
        _sessionmaker_admin = async_sessionmaker(_engine_admin, expire_on_commit=False)
    return _engine_admin


def _maker_admin() -> async_sessionmaker[AsyncSession]:
    engine_admin_instancia()
    assert _sessionmaker_admin is not None
    return _sessionmaker_admin

#Correcion: Engine usuario  
@asynccontextmanager
async def sesion_tenant(tenant_id: str, actor: str = "sistema") -> AsyncIterator[AsyncSession]:
    """Sesión transaccional confinada al tenant (RLS) con actor para triggers.

    Parámetros:
        tenant_id: id de la organización (claim `org` del JWT).
        actor: identidad para el historial (user:<id> | svc:<agente> | sistema);
               lo leen los triggers (T8) vía current_setting('app.actor').
    """
    async with _maker_app()() as db:
        async with db.begin():
            await db.execute(text("SELECT set_config('app.tenant_id', :t, true)"),
                           {"t": tenant_id})
            await db.execute(text("SELECT set_config('app.actor', :a, true)"),
                           {"a": actor})
            yield db

#Correcion: Engine admin
@asynccontextmanager
async def sesion_sistema() -> AsyncIterator[AsyncSession]:
    """Sesión sin confinamiento de tenant (usuario con BYPASSRLS).

    Solo para: recepción de webhooks (aún sin tenant resuelto), workers que
    recorren todos los tenants (billing_cycle, housekeeping) y salud.
    """
    async with _maker_admin()() as db:
        async with db.begin():
            yield db


async def uno(db: AsyncSession, sql: str, params: dict[str, Any] | None = None) -> Any | None:
    """Ejecuta y devuelve la primera fila como mapping (o None)."""
    r = await db.execute(text(sql), params or {})
    fila = r.mappings().first()
    return dict(fila) if fila else None


async def todos(db: AsyncSession, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
    r = await db.execute(text(sql), params or {})
    return [dict(f) for f in r.mappings().all()]


async def valor(db: AsyncSession, sql: str, params: dict[str, Any] | None = None) -> Any:
    r = await db.execute(text(sql), params or {})
    return r.scalar()