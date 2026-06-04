# app/utils.py
import socket
import io
import base64
import qrcode

def obtener_ip_local() -> str:
    """Detecta de forma automática la IP privada del servidor en la red local."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        s.close()
    return ip_local

def generar_qr_base64(contenido: str) -> str:
    """Genera un código QR en memoria y lo devuelve estructurado en formato Base64 para HTML."""
    # Configuración del diseño del QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(contenido)
    qr.make(fit=True)

    # Crear la imagen en memoria usando Pillow
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en un buffer de bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Codificar a Base64 string
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"

def obtener_ip_local() -> str:
    """Detecta de forma automática la IP privada del servidor en la red local."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No se realiza una conexión real; solo sirve para que el OS asigne la interfaz de red activa
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        s.close()
    return ip_local
