from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine_main, engine_logs, Base
from app.models.usuario import Usuario, TokenAcceso
from app.models.log import RegistroLog
from app.utils import obtener_ip_local

# Importamos los nuevos enrutadores modularizados
from app.routers import pwa, setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Verificando y creando bases de datos locales (negocio.db y logs.db)...")
    Base.metadata.create_all(bind=engine_main)
    Base.metadata.create_all(bind=engine_logs)
    print("¡Bases de datos listas y configuradas en Modo WAL!")
    
    ip_servidor = obtener_ip_local()
    print("\n" + "="*60)
    print(f"🚀 ¡Sistema Vita operativo en Red Local DUAL!")
    print(f"🔒 Acceso PWA Seguro:       https://{ip_servidor}:5000")
    print(f"📥 Configuración/Guía HTTP:  http://{ip_servidor}:8000/tutorial")
    print("="*60 + "\n")
    
    yield
    print("Apagando el servidor de forma segura...")

app = FastAPI(
    title="Sistema Vita",
    description="Sistema de gestión interna ultra-ligero para local comercial",
    version="2.0.0",
    lifespan=lifespan
)

# Configuración única de recursos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registro de enrutadores independientes
app.include_router(pwa.router)
app.include_router(setup.router)
