# generar_ssl.py
import datetime
import os
import ipaddress
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def obtener_ip_local() -> str:
    """Detecta de forma automática la IP privada activa para inyectarla en el certificado."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        s.close()
    return ip_local

def crear_certificado_autofirmado():
    # 1. Generar la clave privada
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Configurar los detalles del emisor/sujeto
    sujeto = emisor = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Santiago"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sistema Vita CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Sistema Vita Root CA"),
    ])

    # 3. Configurar nombres alternativos (Dinámicos y precisos)
    nombres_alternativos = [
        x509.DNSName("localhost"),
    ]
    
    # Detectamos la IP real actual del servidor (ej. 192.168.100.67)
    ip_actual = obtener_ip_local()
    
    # Lista base que incluye la IP real detectada y el loopback estándar
    ips_validar = ["127.0.0.1", ip_actual]
    
    for ip in ips_validar:
        try:
            nombres_alternativos.append(x509.IPAddress(ipaddress.ip_address(ip)))
        except ValueError:
            pass

    # 4. Construir el certificado utilizando fechas conscientes de la zona horaria (UTC)
    ahora = datetime.datetime.now(datetime.timezone.utc)
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(sujeto)
    builder = builder.issuer_name(emisor)
    builder = builder.public_key(clave_privada.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(ahora - datetime.timedelta(days=1))
    builder = builder.not_valid_after(ahora + datetime.timedelta(days=3650)) # 10 años
    
    # Nombres Alternativos del Sujeto (SAN)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(nombres_alternativos),
        critical=False
    )

    # 🚨 RESTRICCIÓN CRUCIAL PARA ANDROID 🚨
    # Le dice explícitamente al sistema operativo que este archivo es una Autoridad de Certificación Raíz legítima.
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), 
        critical=True
    )

    # Uso de la Llave: Obligatorio para certificar firmas digitales e infraestructura local
    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,  # Permite validar la autoconexión HTTPS
            crl_sign=True,       # Requisito estructural adicional
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True
    )

    certificado = builder.sign(clave_privada, hashes.SHA256())

    # 5. Guardar archivos en el disco
    os.makedirs("certificados", exist_ok=True)

    with open("certificados/key.pem", "wb") as f:
        f.write(clave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("certificados/cert.pem", "wb") as f:
        f.write(certificado.public_bytes(serialization.Encoding.PEM))

    print("\n" + "="*60)
    print("🔑 ¡Nuevos Certificados CA Raíz generados exitosamente!")
    print(f"📌 IP Local Inyectada: {ip_actual}")
    print("="*60 + "\n")

if __name__ == "__main__":
    crear_certificado_autofirmado()

