# generar_ssl.py
import datetime
import os
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def crear_certificado_autofirmado():
    # 1. Generar la clave privada
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Configurar los detalles del emisor/sujeto (Genérico)
    sujeto = emisor = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Santiago"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sistema Vita"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    # 3. Configurar nombres alternativos (Crucial para que los teléfonos acepten la IP)
    nombres_alternativos = [
        x509.DNSName("localhost"),
    ]
    
    # Agregamos IPs comunes de redes locales como alternativas aceptadas
    ips_locales = ["127.0.0.1", "192.168.0.100", "192.168.1.100", "192.168.1.50"]
    for ip in ips_locales:
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
    builder = builder.add_extension(
        x509.SubjectAlternativeName(nombres_alternativos),
        critical=False
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

    print("🔑 Certificados SSL genéricos generados exitosamente en la carpeta './certificados/'")

if __name__ == "__main__":
    crear_certificado_autofirmado()
