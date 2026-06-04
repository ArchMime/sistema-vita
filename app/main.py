# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Traemos los motores y las bases declarativas corregidas
from app.database import engine_main, engine_logs, BaseMain, BaseLogs
from app.utils import obtener_ip_local
from app.routers import pwa, setup

# Configuración del logger nativo para producción
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SistemaVita")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP] Inicialización asíncrona y segura de tablas aisladas
    logger.info("Verificando bases de datos locales independientes...")
    
    async with engine_main.begin() as conn:
        # Crea SOLO las tablas del negocio en negocio.db
        await conn.run_sync(BaseMain.metadata.create_all)
        
    async with engine_logs.begin() as conn:
        # Crea SOLO las tablas de auditoría en logs.db
        await conn.run_sync(BaseLogs.metadata.create_all)
        
    logger.info("¡Bases de datos listas y optimizadas en Modo WAL!")
    
    # Notificación informativa de red local
    ip_servidor = obtener_ip_local()
    print("\n" + "="*60)
    print(f"🚀 ¡Sistema Vita operativo en Red Local DUAL!")
    print(f"🔒 Acceso PWA Seguro:       https://{ip_servidor}:5000")
    print(f"📥 Configuración/Guía HTTP:  http://{ip_servidor}:8000/tutorial")
    print("="*60 + "\n")
    
    yield
    # [SHUTDOWN] Cierre limpio de recursos
    logger.info("Cerrando conexiones de base de datos de manera segura...")
    await engine_main.dispose()
    await engine_logs.dispose()
    logger.info("Servidor apagado con éxito.")

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Sistema Vita",
    description="Sistema de gestión interna ultra-ligero enfocado en locales comerciales",
    version="2.0.0",
    lifespan=lifespan
)

# Servir archivos estáticos del sistema
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Inyección modular de enrutadores independientes
app.include_router(pwa.router)
app.include_router(setup.router)
