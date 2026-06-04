# app/models/usuario.py
# (No modificar las importaciones si ya las tienes, pero asegúrate de que queden así)
import socket
import io
import base64
import qrcode

def obtener_ip_local() -> str:
    """Detecta de forma automática la IP privada del servidor en la red local.
    
    No realiza una conexión real hacia el exterior; solo se usa para identificar 
    la interfaz de red activa del sistema operativo de forma dinámica.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local: str = s.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        s.close()
    return ip_local

def generar_qr_base64(contenido: str) -> str:
    """Genera un código QR optimizado en memoria RAM.
    
    Devuelve la cadena estructurada en formato Base64 lista para ser inyectada 
    directamente en las etiquetas <img> de las plantillas HTML.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,  # Reducido sutilmente de 10 a 8 para disminuir los bytes de la imagen
        border=3,    # Margen compacto para aprovechar mejor el espacio móvil
    )
    qr.add_data(contenido)
    qr.make(fit=True)

    # Renderizar imagen monocromática ultraligera
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en buffer intermedio optimizando la velocidad de transferencia
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)  # Activa optimización nativa de Pillow
    
    # Codificar a cadena de texto Base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
