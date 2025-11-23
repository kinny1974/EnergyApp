

import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.data.database import get_db
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

# Definimos el Router explícitamente
router = APIRouter()


class OutlierRequest(BaseModel):
    base_year: int
    start_date: str  # formato YYYY-MM-DD
    end_date: str    # formato YYYY-MM-DD
    threshold: float

class MaxPowerRequest(BaseModel):
    device_id: str
    start_date: str  # formato YYYY-MM-DD
    end_date: str    # formato YYYY-MM-DD

class TotalEnergyRequest(BaseModel):
    device_id: str
    start_date: str  # formato YYYY-MM-DD
    end_date: str    # formato YYYY-MM-DD

class DemandGrowthRequest(BaseModel):
    current_period_start: str  # formato YYYY-MM-DD
    current_period_end: str    # formato YYYY-MM-DD
    previous_period_start: str # formato YYYY-MM-DD
    previous_period_end: str   # formato YYYY-MM-DD
    min_growth_percentage: float = 0.0  # porcentaje mínimo de crecimiento

@router.post("/analyze-outliers")
def analyze_outliers(req: OutlierRequest, db: Session = Depends(get_db)):
    """Busca medidores con desviaciones mayores al umbral en el rango de fechas dado."""
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    try:
        resultados = service.find_outlier_devices(
            base_year=req.base_year,
            start_date=req.start_date,
            end_date=req.end_date,
            threshold=req.threshold
        )
        return {"outliers": resultados}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/max-power")
def get_max_power(req: MaxPowerRequest, db: Session = Depends(get_db)):
    """Obtiene la máxima potencia (kW) de un medidor en un periodo específico."""
    repo = EnergyRepository(db)
    try:
        # Validar que el medidor existe
        if not repo.validate_device_id(req.device_id):
            raise HTTPException(status_code=404, detail=f"Medidor {req.device_id} no encontrado")
        
        result = repo.get_max_power_in_period(
            device_id=req.device_id,
            start_date=req.start_date,
            end_date=req.end_date
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el periodo especificado")
        
        return {"max_power_data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/total-energy")
def get_total_energy(req: TotalEnergyRequest, db: Session = Depends(get_db)):
    """Obtiene la energía total consumida (kWh) de un medidor en un periodo específico."""
    repo = EnergyRepository(db)
    try:
        # Validar que el medidor existe
        if not repo.validate_device_id(req.device_id):
            raise HTTPException(status_code=404, detail=f"Medidor {req.device_id} no encontrado")
        
        result = repo.get_total_energy_in_period(
            device_id=req.device_id,
            start_date=req.start_date,
            end_date=req.end_date
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el periodo especificado")
        
        return {"total_energy_data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Esquema para el chatbot ---
class ChatRequest(BaseModel):
    message: str
    context: dict = None
# --- Endpoint de Chatbot ---
@router.post("/chat")
def chat_with_bot(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Crear instancias con dependencia de base de datos
        repo = EnergyRepository(db)
        energy_service = EnergyService(repo)
        chat_service = ChatService(energy_service)
        
        # Limitar longitud del mensaje para evitar bloqueos
        if len(req.message) > 1000:
            return {
                "response": "❌ **Error:** El mensaje es demasiado largo. Por favor, acórtalo.",
                "parameters": None,
                "type": "error"
            }
        
        result = chat_service.ask_gemini(req.message, req.context)
        return result
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return {
                "response": "❌ **Timeout:** La consulta tardó demasiado tiempo. Intenta con una consulta más específica.",
                "parameters": None,
                "type": "error"
            }
        elif "database" in error_msg.lower():
            return {
                "response": "❌ **Error de BD:** Problema de conexión con la base de datos.",
                "parameters": None,
                "type": "error"
            }
        else:
            return {
                "response": f"❌ **Error:** {error_msg}",
                "parameters": None,
                "type": "error"
            }

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

@router.get("/available-data")
def get_available_data_summary(db: Session = Depends(get_db)):
    """Obtiene un resumen de medidores y periodos con datos disponibles."""
    from sqlalchemy import text
    try:
        # Obtener medidores con datos usando SQL nativo
        query = text("""
        SELECT DISTINCT m.deviceid, m.description, 
               MIN(DATE(ml.fecha)) as fecha_min, 
               MAX(DATE(ml.fecha)) as fecha_max,
               COUNT(ml.fecha) as total_lecturas
        FROM public.medidor m 
        JOIN public.m_lecturas ml ON m.deviceid = ml.deviceid 
        GROUP BY m.deviceid, m.description 
        ORDER BY total_lecturas DESC 
        LIMIT 10
        """)
        
        result = db.execute(query)
        devices_data = []
        
        for row in result:
            devices_data.append({
                'deviceid': row[0],
                'description': row[1] if row[1] else 'Sin descripción', 
                'fecha_min': str(row[2]) if row[2] else 'N/A',
                'fecha_max': str(row[3]) if row[3] else 'N/A',
                'total_lecturas': row[4] if row[4] else 0
            })
        
        return {
            "available_devices": devices_data,
            "total_devices": len(devices_data),
            "message": "Medidores con más datos disponibles"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error obteniendo datos: {str(e)}")

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

@router.post("/demand-growth")
def analyze_demand_growth(req: DemandGrowthRequest, db: Session = Depends(get_db)):
    """Analiza el crecimiento de demanda entre dos periodos comparables."""
    repo = EnergyRepository(db)
    service = EnergyService(repo)
    try:
        resultados = service.analyze_demand_growth(
            current_period_start=req.current_period_start,
            current_period_end=req.current_period_end,
            previous_period_start=req.previous_period_start,
            previous_period_end=req.previous_period_end,
            min_growth_percentage=req.min_growth_percentage
        )
        return {"growth_analysis": resultados}
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