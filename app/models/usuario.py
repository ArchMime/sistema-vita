# app/models/usuario.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
# Importamos la base declarativa del núcleo del negocio
from app.database import BaseMain

class Usuario(BaseMain):
    """Representa un usuario del sistema (negocio.db)."""
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True) # Añadido índice para agilizar el login
    rol: Mapped[str] = mapped_column(String(20), server_default='OPERADOR')
    activo: Mapped[bool] = mapped_column(Boolean, server_default=text('1'))

    # Relación bidireccional moderna con los tokens
    tokens: Mapped[List["TokenAcceso"]] = relationship(back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario {self.nombre} (Rol: {self.rol})>"


class TokenAcceso(BaseMain):
    """Almacena los tokens de sesión vinculados a teléfonos específicos (negocio.db)."""
    __tablename__ = 'tokens_acceso'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True) # Añadido índice para búsquedas de sesión instantáneas
    dispositivo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('usuarios.id'), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, server_default=text('1'), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    # Relación inversa
    usuario: Mapped[Optional["Usuario"]] = relationship(back_populates="tokens")

    def __repr__(self) -> str:
        return f"<TokenAcceso ID: {self.id} - Activo: {self.activo}>"
