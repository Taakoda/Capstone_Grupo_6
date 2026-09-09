# tests/conftest.py
import uuid

import pytest_asyncio
from kallicode_core.db import (
    engine_admin_instancia,
    engine_app_instancia,
    sesion_sistema,
    sesion_tenant,
)
from sqlalchemy import text


@pytest_asyncio.fixture
async def db_engine_app():
    return engine_app_instancia()


@pytest_asyncio.fixture
async def db_engine_admin():
    return engine_admin_instancia()


@pytest_asyncio.fixture
async def tenant_a():
    tenant_id = f"org_test_{uuid.uuid4().hex[:12]}"
    async with sesion_sistema() as db:
        await db.execute(
            text("INSERT INTO core.organizations (id, nombre) VALUES (:id, 'Tenant A Test')"),
            {"id": tenant_id},
        )
    yield tenant_id
    async with sesion_sistema() as db:
        await db.execute(text("DELETE FROM core.tickets WHERE tenant_id = :id"), {"id": tenant_id})
        await db.execute(
            text("DELETE FROM core.ticket_counters WHERE tenant_id = :id"), {"id": tenant_id}
        )
        await db.execute(text("DELETE FROM core.users WHERE tenant_id = :id"), {"id": tenant_id})
        await db.execute(text("DELETE FROM core.organizations WHERE id = :id"), {"id": tenant_id})


@pytest_asyncio.fixture
async def tenant_b():
    tenant_id = f"org_test_{uuid.uuid4().hex[:12]}"
    async with sesion_sistema() as db:
        await db.execute(
            text("INSERT INTO core.organizations (id, nombre) VALUES (:id, 'Tenant B Test')"),
            {"id": tenant_id},
        )
    yield tenant_id
    async with sesion_sistema() as db:
        await db.execute(text("DELETE FROM core.tickets WHERE tenant_id = :id"), {"id": tenant_id})
        await db.execute(
            text("DELETE FROM core.ticket_counters WHERE tenant_id = :id"), {"id": tenant_id}
        )
        await db.execute(text("DELETE FROM core.users WHERE tenant_id = :id"), {"id": tenant_id})
        await db.execute(text("DELETE FROM core.organizations WHERE id = :id"), {"id": tenant_id})


@pytest_asyncio.fixture
async def datos_equivalentes(tenant_a, tenant_b):
    ticket_a = f"tk_{uuid.uuid4().hex[:12]}"
    ticket_b = f"tk_{uuid.uuid4().hex[:12]}"
    user_a = f"u_{uuid.uuid4().hex[:12]}"
    user_b = f"u_{uuid.uuid4().hex[:12]}"

    async with sesion_sistema() as db:
        await db.execute(
            text("""INSERT INTO core.users (id, tenant_id, email, nombre, rol)
                    VALUES (:id, :t, :email, 'Test User', 'member')"""),
            {"id": user_a, "t": tenant_a, "email": f"{user_a}@test.local"},
        )
        await db.execute(
            text("""INSERT INTO core.users (id, tenant_id, email, nombre, rol)
                    VALUES (:id, :t, :email, 'Test User', 'member')"""),
            {"id": user_b, "t": tenant_b, "email": f"{user_b}@test.local"},
        )

    async with sesion_tenant(tenant_a) as db:
        await db.execute(
            text("""INSERT INTO core.tickets (id, tenant_id, tipo, titulo, descripcion, reportado_por)
                    VALUES (:id, :t, 'bug', 'Ticket A', 'desc A', :u)"""),
            {"id": ticket_a, "t": tenant_a, "u": user_a},
        )
    async with sesion_tenant(tenant_b) as db:
        await db.execute(
            text("""INSERT INTO core.tickets (id, tenant_id, tipo, titulo, descripcion, reportado_por)
                    VALUES (:id, :t, 'bug', 'Ticket B', 'desc B', :u)"""),
            {"id": ticket_b, "t": tenant_b, "u": user_b},
        )

    return {"ticket_a": ticket_a, "ticket_b": ticket_b, "user_a": user_a, "user_b": user_b}
