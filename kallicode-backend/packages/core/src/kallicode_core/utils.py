def clave_redis(tenant_id: str, *partes: str) -> str:
    """
    construye una clave de redis prefijada obligatoriamente al tenant_id
    de la organizacion. Fuerza el aislamiento de datos de cada tenant
    (Hallazgo BE-F03)
    """
    if not tenant_id:
        raise ValueError("El tenant_id es obligatorio para construir la clave de redis.")

    #une las partes con ":" (ej: "prefligh:KC-1045:produccion")
    sufijo = ":".join(str(p) for p in partes if p is not None)

    #retorna la clave final aislada (ej: "empresa_A:prefligh:KC-1045:produccion")
    return f"{tenant_id}:{sufijo}" 
