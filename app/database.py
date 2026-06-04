# app/database.py
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Configuración centralizada (Fácil migración a variables de entorno o archivo .env a futuro)
DB_MAIN_URL = "sqlite+aiosqlite:///./negocio.db"
DB_LOGS_URL = "sqlite+aiosqlite:///./logs.db"

# Argumentos de conexión optimizados para bajo consumo y concurrencia local
CONNECT_ARGS = {
    "check_same_thread": False, 
    "timeout": 20.0
}

# 1. Motores Asíncronos Independientes
engine_main = create_async_engine(DB_MAIN_URL, connect_args=CONNECT_ARGS)
engine_logs = create_async_engine(DB_LOGS_URL, connect_args=CONNECT_ARGS)

# 2. Bases Declarativas Separadas (Evita mezclar tablas de auditoría con las de negocio)
class BaseMain(DeclarativeBase):
    """Modelos del núcleo del negocio (negocio.db)"""
    pass

class BaseLogs(DeclarativeBase):
    """Modelos exclusivos para logs y auditoría (logs.db)"""
    pass

# 3. Optimizador de Rendimiento: Forzar Modo WAL de forma asíncrona al conectar
async def configurar_sqlite_wal(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")  # Acelera escrituras en discos lentos
    cursor.close()

# Registramos los optimizadores en ambos motores
from sqlalchemy import event
event.listen(engine_main.sync_engine, "connect", lambda conn, rec: conn.cursor().execute("PRAGMA journal_mode=WAL;"))
event.listen(engine_logs.sync_engine, "connect", lambda conn, rec: conn.cursor().execute("PRAGMA journal_mode=WAL;"))

# 4. Generadores de sesiones asíncronas
SessionMain = async_sessionmaker(bind=engine_main, expire_on_commit=False)
SessionLogs = async_sessionmaker(bind=engine_logs, expire_on_commit=False)

# 5. Dependencias (Inyección de Dependencias limpia para FastAPI Routers)
async def get_db_main() -> AsyncSession:
    """Provee una sesión asíncrona para la base de datos de negocio."""
    async with SessionMain() as session:
        yield session

async def get_db_logs() -> AsyncSession:
    """Provee una sesión asíncrona exclusiva para el registro de auditorías."""
    async with SessionLogs() as session:
        yield session

