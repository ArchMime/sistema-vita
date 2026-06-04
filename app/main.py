# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.database import engine_main, engine_logs, Base
# Importamos los modelos para que SQLAlchemy sepa que existen al crear las tablas
from app.models.usuario import Usuario, TokenAcceso
from app.models.log import RegistroLog

# Importamos la función utilitaria de detección de IP
from app.utils import obtener_ip_local, generar_qr_base64
# Definimos la ruta al certificado SSL en la raíz del proyecto
CERT_PATH = os.path.join("certificados", "cert.pem")

# 1. Ciclo de vida de la aplicación (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP]: Se ejecuta al encender el servidor
    print("Verificando y creando bases de datos locales (negocio.db y logs.db)...")
    
    # Crea las tablas correspondientes en cada archivo independiente si no existen
    Base.metadata.create_all(bind=engine_main)
    Base.metadata.create_all(bind=engine_logs)
    print("¡Bases de datos listas y configuradas en Modo WAL!")
    
    # Mensaje informativo en consola con la IP real detectada en tu red local
    ip_servidor = obtener_ip_local()
    print("\n" + "="*60)
    print(f"🚀 ¡Sistema Vita operativo en Red Local DUAL!")
    print(f"🔒 Acceso PWA Seguro:       https://{ip_servidor}:5000")
    print(f"📥 Descarga HTTP (Limpia):  http://{ip_servidor}:8000/descargar-certificado")
    print("="*60 + "\n")
    
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

# 4. Rutas y Endpoints

@app.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    """Sirve la página de inicio. Redirige a HTTPS si entran por el puerto HTTP."""
    ip_servidor = obtener_ip_local()
    
    # Si entran por HTTP ordinario (Puerto 8000), los mandamos forzosamente al HTTPS seguro (Puerto 5000)
    if request.url.scheme == "http":
        return RedirectResponse(url=f"https://{ip_servidor}:5000/")
    
    # URLs dinámicas basadas en la IP del servidor
    url_certificado = f"http://{ip_servidor}:8000/descargar-certificado"
    url_pwa = f"https://{ip_servidor}:5000/"
    
    # Generamos ambos códigos QR de manera independiente en la RAM
    qr_certificado = generar_qr_base64(url_certificado)
    qr_navegacion = generar_qr_base64(url_pwa)  # <-- Inyección del nuevo QR
    
    contexto = {
        "request": request,
        "ip_servidor": ip_servidor,
        "url_certificado": url_certificado,
        "url_pwa": url_pwa,
        "qr_certificado": qr_certificado,
        "qr_navegacion": qr_navegacion     # <-- Enviado a la plantilla HTML
    }
    
    return templates.TemplateResponse(name="index.html", context=contexto)


@app.get("/descargar-certificado")
async def descargar_certificado():
    """Sirve el archivo cert.pem renombrado como archivo .crt. Accesible por HTTP y HTTPS."""
    if not os.path.exists(CERT_PATH):
        return {"error": "El certificado SSL no se encuentra en el servidor. Ejecuta generar_ssl.py primero."}
        
    return FileResponse(
        path=CERT_PATH,
        media_type="application/x-x509-ca-cert",
        filename="sistema_vita_root.crt"
    )
