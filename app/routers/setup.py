# app/routers/setup.py
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.utils import obtener_ip_local
import anyio

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Definición de rutas absoluta y limpia basada en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CERT_PATH = BASE_DIR / "certificados" / "cert.pem"

@router.get("/tutorial", response_class=HTMLResponse)
async def mostrar_tutorial(request: Request):
    """Sirve la guía interactiva paso a paso para la instalación del certificado."""
    ip_servidor = obtener_ip_local()
    url_pwa = f"https://{ip_servidor}:5000/"
    
    return templates.TemplateResponse(
        name="tutorial.html", 
        context={
            "request": request, 
            "url_pwa": url_pwa
        }
    )

@router.get("/descargar-certificado")
async def descargar_certificado():
    """Sirve el archivo cert.pem renombrado como archivo .crt para los teléfonos de forma asíncrona."""
    # Verificación de archivo de forma asíncrona (No bloquea el bucle de eventos de FastAPI)
    try:
        existe_certificado = await anyio.to_thread.run_sync(CERT_PATH.exists)
    except Exception:
        existe_certificado = False

    if not existe_certificado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El certificado SSL no se encuentra en el servidor. Ejecuta generar_ssl.py primero."
        )
        
    return FileResponse(
        path=CERT_PATH,
        media_type="application/x-x509-ca-cert",
        filename="sistema_vita_root.crt"
    )
