import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Energy N-Tier System"
    PROJECT_VERSION: str = "1.0.0"
    
    # Conexión a Base de Datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://administrador:marcela2025@localhost:5432/sgcnmdb"
    )

settings = Settings()