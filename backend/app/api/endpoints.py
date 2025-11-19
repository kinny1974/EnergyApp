import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.data.database import get_db
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService

# Definimos el Router explícitamente
router = APIRouter()

# --- Esquemas Pydantic ---
class AnalysisReq(BaseModel):
    device_id: str
    base_year: int
    target_date: str

# --- Rutas (Usando @router) ---

@router.post("/upload/{device_id}")
async def upload_readings(
    device_id: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        repo = EnergyRepository(db)
        service = EnergyService(repo)
        
        return service.process_csv_upload(df, device_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/years-from-csv")
async def get_years_from_csv(file: UploadFile = File(...)):
    """Extrae los años únicos de un archivo CSV de lecturas."""
    try:
        service = EnergyService(None) # No se necesita repo para esta operación
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        return service.get_years_from_dataframe(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {e}")

@router.get("/years/{device_id}")
def get_available_years(device_id: str, db: Session = Depends(get_db)):
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    service.validate_device(device_id)
    return {"years": repo.get_available_years(device_id)}

@router.get("/devices")
def get_available_devices(db: Session = Depends(get_db)):
    """Obtiene lista de medidores disponibles."""
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    return {"devices": service.get_available_devices()}

@router.get("/devices/{device_id}")
def get_device_info(device_id: str, db: Session = Depends(get_db)):
    """Obtiene información de un medidor específico."""
    repo = EnergyRepository(db)
    medidor = repo.get_medidor(device_id)
    if not medidor:
        raise HTTPException(status_code=404, detail=f"Medidor {device_id} no encontrado")
    
    return {
        "deviceid": medidor.deviceid,
        "description": medidor.description,
        "devicetype": medidor.devicetype,
        "customerid": medidor.customerid,
        "usergroup": medidor.usergroup,
        "connectiontype": medidor.connectiontype,
        "id_loc": medidor.id_loc,
        "id_cen": medidor.id_cen
    }

@router.post("/analyze")
def analyze_energy(req: AnalysisReq, db: Session = Depends(get_db)):
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    try:
        return service.analyze_day(
            req.device_id,
            req.target_date,
            req.base_year
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze-with-file")
async def analyze_energy_with_file(
    db: Session = Depends(get_db),
    device_id: str = Form(...),
    base_year: int = Form(...),
    target_date: str = Form(...),
    base_file: UploadFile = File(...)
):
    """Ejecuta el análisis usando un archivo CSV como base histórica."""
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    try:
        content = await base_file.read()
        base_df = pd.read_csv(io.StringIO(content.decode('utf-8')))

        return service.analyze_day_with_df(
            device_id=device_id,
            target_date_str=target_date,
            base_year=base_year,
            base_df=base_df
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))