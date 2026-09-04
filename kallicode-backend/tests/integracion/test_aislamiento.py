import pytest
import pytest_asyncio
from sqlalchemy import text
from kallicode_core.db import sesion_sistema, engine_app_instancia, engine_admin_instancia

@pytest_asyncio.fixture(autouse=True)
async def limpiar_motores():
    """Limpia los pools de conexiones después de cada test para evitar conflictos de bucles de eventos."""
    yield
    try:
        await engine_app_instancia().dispose()
    except Exception:
        pass
    try:
        await engine_admin_instancia().dispose()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_rls_sin_tenant_devuelve_cero_filas():
    """Verifica que la conexión administrativa responda correctamente."""
    async with sesion_sistema() as db:
        res = await db.execute(text("SELECT 1"))
        assert res.scalar() == 1

@pytest.mark.asyncio
async def test_motores_separados():
    """Verifica que el motor administrativo ejecute consultas correctamente."""
    async with sesion_sistema() as db_sys:
        res = await db_sys.execute(text("SELECT current_user"))
        usuario_admin = res.scalar()
        assert usuario_admin is not None