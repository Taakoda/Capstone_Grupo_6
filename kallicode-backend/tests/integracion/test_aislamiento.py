from kallicode_core.db import sesion_tenant
from sqlalchemy import text

TABLAS_CON_TENANT_ID = [
    "core.tickets",
    "core.jobs",
    "core.users",
    "core.connections",
    "core.notifications",
    "core.usage_tokens",
    "core.security_findings",
    "core.gate_signatures",
]


async def test_sesion_app_sin_tenant_no_ve_nada(db_engine_app):
    """Sin app.tenant_id seteado, kallicode_app_local no debe ver
    ninguna fila en tablas con RLS activo."""
    async with db_engine_app.connect() as conn:
        for tabla in ("core.tickets", "core.jobs", "audit.audit_events"):
            resultado = await conn.execute(text(f"SELECT * FROM {tabla}"))
            filas = resultado.fetchall()
            assert filas == [], f"{tabla} devolvió filas sin tenant_id seteado"


async def test_rls_no_cruza_tenants_multi_tabla(tenant_a, tenant_b, datos_equivalentes):
    """El tenant B nunca debe ver filas del tenant A en ninguna tabla con RLS."""
    async with sesion_tenant(tenant_b) as db:
        for tabla in TABLAS_CON_TENANT_ID:
            r = await db.execute(text(f"SELECT tenant_id FROM {tabla}"))
            filas = r.mappings().all()
            for fila in filas:
                assert fila["tenant_id"] == tenant_b, (
                    f"{tabla}: tenant B vio una fila con tenant_id={fila['tenant_id']}"
                )


async def test_rol_app_no_tiene_bypassrls(db_engine_app):
    async with db_engine_app.connect() as conn:
        r = await conn.execute(
            text("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
        )
        fila = r.fetchone()
        assert fila.rolbypassrls is False, "kallicode_app_local tiene BYPASSRLS activo"
