# app/models/log.py
from datetime import datetime
from sqlalchemy import String, Integer, text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.database import Base

class RegistroLog(Base):
    """Esquema de auditoría aislado para operaciones rápidas (logs.db)."""
    __tablename__ = "logs_operaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_hora: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True) # Indexado para buscar rápido
    tabla_afectada: Mapped[str] = mapped_column(String(50), nullable=False)
    registro_id: Mapped[int] = mapped_column(Integer, nullable=False)
    accion: Mapped[str] = mapped_column(String(20), nullable=False) # 'CREAR', 'MODIFICAR', 'ANULAR'
    detalles: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Para JSON o texto extra

    def __repr__(self) -> str:
        return f"<Log {self.accion} en {self.tabla_afectada} por Usuario {self.usuario_id}>"
