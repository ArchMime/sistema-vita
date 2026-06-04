# app/routers/pwa.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import obtener_ip_local, generar_qr_base64
import anyio

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Configuración centralizada de puertos (Fácil de mover a un .env a futuro)
PUERTO_HTTP = 8000
PUERTO_HTTPS = 5000

@router.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    """Sirve la página de inicio de la PWA de forma optimizada y no bloqueante.
    
    Redirige al tutorial interactivo si entran por el canal inseguro (HTTP).
    """
    ip_servidor = obtener_ip_local()
    
    # Redirección inteligente si acceden por HTTP ordinario
    if request.url.scheme == "http":
        return RedirectResponse(url=f"http://{ip_servidor}:{PUERTO_HTTP}/tutorial")
    
    url_certificado = f"http://{ip_servidor}:{PUERTO_HTTP}/tutorial"
    url_pwa = f"https://{ip_servidor}:{PUERTO_HTTPS}/"
    
    # Optimizacion de CPU: Ejecutamos la carga pesada de imágenes en hilos separados en paralelo
    async with anyio.create_task_group() as tg:
        async def obtener_qr_cert():
            nonlocal qr_certificado
            qr_certificado = await anyio.to_thread.run_sync(generar_qr_base64, url_certificado)
            
        async def obtener_qr_nav():
            nonlocal qr_navegacion
            qr_navegacion = await anyio.to_thread.run_sync(generar_qr_base64, url_pwa)
            
        # Lanzamos ambas tareas concurrentemente
        tg.start_soon(obtener_qr_cert)
        tg.start_soon(obtener_qr_nav)
    
    contexto = {
        "request": request,
        "ip_servidor": ip_servidor,
        "url_certificado": url_certificado,
        "url_pwa": url_pwa,
        "qr_certificado": qr_certificado,
        "qr_navegacion": qr_navegacion 
    }
    
    return templates.TemplateResponse(name="index.html", context=contexto)
