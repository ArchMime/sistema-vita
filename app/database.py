# app/database.py
import sqlalchemy.event as event
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Rutas locales para tus dos archivos SQLite
DATABASE_URL_MAIN = "sqlite:///./negocio.db"
DATABASE_URL_LOGS = "sqlite:///./logs.db"

# 2. Motores independientes optimizados para PC de bajos recursos
# 'check_same_thread=False' permite que FastAPI use hilos asíncronos de forma segura.
# 'timeout=20.0' hace que los procesos esperen si el disco duro está ocupado (evita caídas).
engine_main = create_engine(
    DATABASE_URL_MAIN, 
    connect_args={"check_same_thread": False, "timeout": 20.0}
)

engine_logs = create_engine(
    DATABASE_URL_LOGS, 
    connect_args={"check_same_thread": False, "timeout": 20.0}
)

# 3. Truco de Rendimiento: Forzar el Modo WAL (Write-Ahead Logging) en SQLite
# Esto permite que los teléfonos lean datos mientras el servidor escribe, sin bloquearse.
def activar_modo_wal(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()

# Escuchamos el evento de conexión para aplicar el modo WAL automáticamente
event.listen(engine_main, "connect", activar_modo_wal)
event.listen(engine_logs, "connect", activar_modo_wal)

# 4. Fábricas de sesiones independientes
SessionLocalMain = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)
SessionLocalLogs = sessionmaker(autocommit=False, autoflush=False, bind=engine_logs)

# 5. Base herendada para mapear los Modelos SQLAlchemy
Base = declarative_base()

# 6. Generadores de Sesión (Las dependencias que usarán tus controladores)
def get_db_main():
    """Abre una conexión para el negocio y la cierra al terminar la petición."""
    db = SessionLocalMain()
    try:
        yield db
    finally:
        db.close()

def get_db_logs():
    """Abre una conexión exclusiva para la auditoría y la cierra al terminar."""
    db = SessionLocalLogs()
    try:
        yield db
    finally:
        db.close()
