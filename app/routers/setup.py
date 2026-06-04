import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.utils import obtener_ip_local

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Buscamos el certificado un directorio arriba porque routers/ está un nivel más profundo
CERT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "certificados", "cert.pem")

@router.get("/tutorial", response_class=HTMLResponse)
async def mostrar_tutorial(request: Request):
    """Sirve la guía interactiva paso a paso para la instalación del certificado."""
    ip_servidor = obtener_ip_local()
    url_pwa = f"https://{ip_servidor}:5000/"
    
    return templates.TemplateResponse(
        name="tutorial.html", 
        context={"request": request, "url_pwa": url_pwa}
    )

@router.get("/descargar-certificado")
async def descargar_certificado():
    """Sirve el archivo cert.pem renombrado como archivo .crt para los teléfonos."""
    if not os.path.exists(CERT_PATH):
        return {"error": "El certificado SSL no se encuentra en el servidor. Ejecuta generar_ssl.py primero."}
        
    return FileResponse(
        path=CERT_PATH,
        media_type="application/x-x509-ca-cert",
        filename="sistema_vita_root.crt"
    )
