# generar_ssl.py
import datetime
from pathlib import Path
import ipaddress

# Importamos la criptografía avanzada de x509
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Reutilizamos la función centralizada para evitar duplicación de código
from app.utils import obtener_ip_local

def crear_certificado_autofirmado():
    # 1. Generar la clave privada RSA de alta seguridad
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Configurar los detalles del emisor y sujeto homogéneo
    sujeto = emisor = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Santiago"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sistema Vita CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Sistema Vita Root CA"),
    ])

    # 3. Configurar nombres alternativos (SAN) para evitar rechazos en el navegador
    nombres_alternativos = [
        x509.DNSName("localhost"),
    ]
    
    # Detectamos la IP dinámica real utilizando el módulo centralizado
    ip_actual = obtener_ip_local()
    ips_validar = ["127.0.0.1", ip_actual]
    
    for ip in ips_validar:
        try:
            nombres_alternativos.append(x509.IPAddress(ipaddress.ip_address(ip)))
        except ValueError:
            pass

    # 4. Construir el certificado con compatibilidad UTC estricta
    ahora = datetime.datetime.now(datetime.timezone.utc)
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(sujeto)
    builder = builder.issuer_name(emisor)
    builder = builder.public_key(clave_privada.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(ahora - datetime.timedelta(days=1))
    builder = builder.not_valid_after(ahora + datetime.timedelta(days=3650)) # 10 años
    
    # Inyección de los nombres alternativos (SAN)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(nombres_alternativos),
        critical=False
    )

    # Marcamos explícitamente como Autoridad Certificadora Raíz (Requisito Android/iOS)
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), 
        critical=True
    )

    # Uso básico de llaves (Firmas y firmas de certificados)
    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True
    )

    # 🎯 CORRECCIÓN CRÍTICA: Añadimos ExtendedKeyUsage para validar autenticación de servidor
    # Esto elimina de forma definitiva el aviso de peligro en Google Chrome móvil
    builder = builder.add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH,
            ExtendedKeyUsageOID.CLIENT_AUTH
        ]),
        critical=False
    )

    # Firmar el certificado usando SHA256
    certificado = builder.sign(clave_privada, hashes.SHA256())

    # 5. Guardar archivos de manera segura usando Pathlib
    carpeta_certificados = Path("certificados")
    carpeta_certificados.mkdir(exist_ok=True)

    ruta_key = carpeta_certificados / "key.pem"
    ruta_cert = carpeta_certificados / "cert.pem"

    ruta_key.write_bytes(clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

    ruta_cert.write_bytes(certificado.public_bytes(serialization.Encoding.PEM))

    print("\n" + "="*60)
    print("🔑 ¡Nuevos Certificados CA Raíz generados con éxito!")
    print("🎯 Compatibilidad con Google Chrome y Safari Móvil Activada.")
    print(f"📌 IP Local Inyectada: {ip_actual}")
    print("="*60 + "\n")

if __name__ == "__main__":
    crear_certificado_autofirmado()
