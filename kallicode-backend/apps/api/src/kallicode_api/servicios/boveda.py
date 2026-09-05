"""Bóveda de secretos.

Local: los secretos viven en Redis con prefijo específico por tenant
(suficiente para desarrollo; NO producción). TODO(produccion): Azure Key Vault vía
azure-keyvault-secrets con managed identity — misma interfaz.
"""
from __future__ import annotations

import json

from kallicode_core.comercial import redis_cliente
from kallicode_core.logging import log
from kallicode_core.utils import clave_redis


async def guardar(tenant_id: str, nombre: str, valor: dict) -> str:
    """Guarda el secreto y devuelve su referencia (lo que persiste la BD)."""
    clave = clave_redis(tenant_id, "boveda", nombre)
    await redis_cliente().set(clave, json.dumps(valor))
    log.info("boveda.guardado", ref=nombre, tenant_id=tenant_id)  # nunca el valor
    return nombre


async def leer(tenant_id: str, nombre: str) -> dict | None:
    clave = clave_redis(tenant_id, "boveda", nombre)
    crudo = await redis_cliente().get(clave)
    return json.loads(crudo) if crudo else None


async def eliminar(tenant_id: str, nombre: str) -> None:
    clave = clave_redis(tenant_id, "boveda", nombre)
    await redis_cliente().delete(clave)
    log.info("boveda.eliminado", ref=nombre, tenant_id=tenant_id)