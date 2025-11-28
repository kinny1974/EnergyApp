from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.config import settings
from app.api import endpoints
from app.data.database import engine, Base

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar Tablas (Opcional: mejor usar migraciones como Alembic en prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Incluir Rutas
app.include_router(endpoints.router)

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor Energy N-Tier...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)