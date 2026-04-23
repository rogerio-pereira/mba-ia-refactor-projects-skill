import system_repository


def get_health_status():
    return {
        "status": "ok",
        "database": "connected",
        "counts": system_repository.get_health_counts(),
        "versao": "1.0.0",
    }
