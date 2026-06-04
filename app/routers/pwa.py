from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils import obtener_ip_local, generar_qr_base64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def leer_index(request: Request):
    """Sirve la página de inicio de la PWA. Redirige al tutorial si entran sin HTTPS."""
    ip_servidor = obtener_ip_local()
    
    # Si entran por HTTP ordinario (Puerto 8000), los mandamos al tutorial interactivo en vez de un redirect ciego
    if request.url.scheme == "http":
        return RedirectResponse(url=f"http://{ip_servidor}:8000/tutorial")
    
    url_certificado = f"http://{ip_servidor}:8000/tutorial"
    url_pwa = f"https://{ip_servidor}:5000/"
    
    qr_certificado = generar_qr_base64(url_certificado)
    qr_navegacion = generar_qr_base64(url_pwa)
    
    contexto = {
        "request": request,
        "ip_servidor": ip_servidor,
        "url_certificado": url_certificado,
        "url_pwa": url_pwa,
        "qr_certificado": qr_certificado,
        "qr_navegacion": qr_navegacion 
    }
    
    return templates.TemplateResponse(name="index.html", context=contexto)
