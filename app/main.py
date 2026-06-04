# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.database import engine_main, engine_logs, Base
# Importamos los modelos para que SQLAlchemy sepa que existen al crear las tablas
from app.models.usuario import Usuario, TokenAcceso
from app.models.log import RegistroLog

# 1. Ciclo de vida de la aplicación (Reemplaza al antiguo 'with app.app_context()')
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP]: Se ejecuta al encender el servidor
    print("Verificando y creando bases de datos locales (negocio.db y logs.db)...")
    
    # Crea las tablas correspondientes en cada archivo independiente si no existen
    Base.metadata.create_all(bind=engine_main)
    Base.metadata.create_all(bind=engine_logs)
    
    print("¡Bases de datos listas y configuradas en Modo WAL!")
    yield
    # [SHUTDOWN]: Se ejecuta al apagar el servidor
    print("Apagando el servidor de forma segura...")

# 2. Inicialización de la Aplicación FastAPI
app = FastAPI(
    title="Sistema Vita",
    description="Sistema de gestión interna ultra-ligero para local comercial",
    version="2.0.0",
    lifespan=lifespan
)

# 3. Configuración de Archivos Estáticos y Plantillas (Vistas HTML)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 4. Ruta Raíz (Sirve la interfaz PWA base)
@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    """Sirve la página de inicio de la interfaz PWA."""
    return templates.TemplateResponse(request=request, name="index.html")

# Nota: Los controladores (Blueprints en Flask) los registraremos aquí 
# usando 'app.include_router()' a medida que los vayamos creando verticalmente.
