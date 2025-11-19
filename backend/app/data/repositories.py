from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.data.models import MLectura, Medidor

class EnergyRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_insert_readings(self, readings: List[MLectura]):
        """Inserta o actualiza lecturas masivamente."""
        try:
            # Usamos merge para manejar duplicados (upsert simple)
            for r in readings:
                self.db.merge(r)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def get_readings_by_date(self, device_id: str, target_date: datetime):
        """Obtiene lecturas de un día completo (00:00 a 23:59)."""
        start = target_date.replace(hour=0, minute=0, second=0)
        end = target_date.replace(hour=23, minute=59, second=59)
        
        return self.db.query(MLectura).filter(
            MLectura.deviceid == device_id,
            MLectura.fecha >= start,
            MLectura.fecha <= end
        ).order_by(MLectura.fecha).all()

    def get_historical_year_data(self, device_id: str, year: int):
        """Obtiene todas las lecturas de un año para calcular la baseline."""
        return self.db.query(MLectura).filter(
            MLectura.deviceid == device_id,
            extract('year', MLectura.fecha) == year
        ).all()
    
    def get_available_years(self, device_id: str):
        """Retorna lista de años disponibles para un dispositivo."""
        years = self.db.query(extract('year', MLectura.fecha)).filter(
            MLectura.deviceid == device_id
        ).distinct().all()
        return sorted([int(y[0]) for y in years])

    # Nuevos métodos para la tabla medidor
    def get_medidor(self, device_id: str) -> Optional[Medidor]:
        """Obtiene un medidor por su deviceid."""
        return self.db.query(Medidor).filter(Medidor.deviceid == device_id).first()

    def get_all_medidores(self) -> List[Medidor]:
        """Obtiene todos los medidores."""
        return self.db.query(Medidor).all()

    def get_active_medidores(self) -> List[Medidor]:
        """Obtiene medidores activos (donde desactivado es NULL)."""
        return self.db.query(Medidor).filter(Medidor.desactivado.is_(None)).all()

    def validate_device_id(self, device_id: str) -> bool:
        """Valida que un deviceid exista en la tabla medidor."""
        medidor = self.get_medidor(device_id)
        return medidor is not None