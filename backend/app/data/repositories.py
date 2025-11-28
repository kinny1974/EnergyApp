from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, func
from app.data.models import MLectura, Medidor, Localidad, Municipio, Departamento

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
    
    def get_readings_range(self, device_id: str, start_date: datetime, end_date: datetime):
        """Obtiene todas las lecturas en un rango de fechas (optimizado para consultas masivas)."""
        return self.db.query(MLectura).filter(
            MLectura.deviceid == device_id,
            MLectura.fecha >= start_date,
            MLectura.fecha < end_date
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
    
    def count_active_medidores(self) -> int:
        """Cuenta el número de medidores activos."""
        return self.db.query(Medidor).filter(Medidor.desactivado.is_(None)).count()

    def validate_device_id(self, device_id: str) -> bool:
        """Valida que un deviceid exista en la tabla medidor."""
        medidor = self.get_medidor(device_id)
        return medidor is not None
    
    # Métodos para localidades, municipios y departamentos
    
    def get_localidad(self, id_loc: str) -> Optional[Localidad]:
        """Obtiene una localidad por su ID."""
        return self.db.query(Localidad).filter(Localidad.id_loc == id_loc).first()
    
    def get_all_localidades(self) -> List[Localidad]:
        """Obtiene todas las localidades con sus relaciones."""
        return self.db.query(Localidad).options(joinedload(Localidad.municipio)).all()
    
    def search_localidades_by_name(self, localidad_name: str) -> List[Localidad]:
        """Busca localidades por nombre (búsqueda parcial, case-insensitive)."""
        return self.db.query(Localidad).filter(
            Localidad.localidad.ilike(f"%{localidad_name}%")
        ).options(joinedload(Localidad.municipio)).all()
    
    def get_medidores_by_localidad(self, localidad_name: str) -> List[Medidor]:
        """Obtiene todos los medidores de una localidad por nombre de localidad."""
        return self.db.query(Medidor).join(
            Localidad, Medidor.id_loc == Localidad.id_loc
        ).filter(
            Localidad.localidad.ilike(f"%{localidad_name}%")
        ).options(joinedload(Medidor.localidad)).all()
    
    def get_medidores_by_localidad_id(self, id_loc: str) -> List[Medidor]:
        """Obtiene todos los medidores de una localidad por ID."""
        return self.db.query(Medidor).filter(
            Medidor.id_loc == id_loc
        ).options(joinedload(Medidor.localidad)).all()
    
    def get_municipio(self, id_mun: str) -> Optional[Municipio]:
        """Obtiene un municipio por su ID."""
        return self.db.query(Municipio).filter(Municipio.id_mun == id_mun).first()
    
    def get_all_municipios(self) -> List[Municipio]:
        """Obtiene todos los municipios con sus relaciones."""
        return self.db.query(Municipio).options(
            joinedload(Municipio.departamento)
        ).all()
    
    def search_municipios_by_name(self, municipio_name: str) -> List[Municipio]:
        """Busca municipios por nombre (búsqueda parcial, case-insensitive)."""
        return self.db.query(Municipio).filter(
            Municipio.municipio.ilike(f"%{municipio_name}%")
        ).options(joinedload(Municipio.departamento)).all()
    
    def get_medidores_by_municipio(self, municipio_name: str) -> List[Medidor]:
        """Obtiene todos los medidores de un municipio."""
        return self.db.query(Medidor).join(
            Localidad, Medidor.id_loc == Localidad.id_loc
        ).join(
            Municipio, Localidad.id_mun == Municipio.id_mun
        ).filter(
            Municipio.municipio.ilike(f"%{municipio_name}%")
        ).options(
            joinedload(Medidor.localidad).joinedload(Localidad.municipio)
        ).all()
    
    def get_departamento(self, id_dep: str) -> Optional[Departamento]:
        """Obtiene un departamento por su ID."""
        return self.db.query(Departamento).filter(Departamento.id_dep == id_dep).first()
    
    def get_all_departamentos(self) -> List[Departamento]:
        """Obtiene todos los departamentos."""
        return self.db.query(Departamento).all()
    
    def search_departamentos_by_name(self, departamento_name: str) -> List[Departamento]:
        """Busca departamentos por nombre (búsqueda parcial, case-insensitive)."""
        return self.db.query(Departamento).filter(
            Departamento.departamento.ilike(f"%{departamento_name}%")
        ).all()
    
    def get_medidores_by_departamento(self, departamento_name: str) -> List[Medidor]:
        """Obtiene todos los medidores de un departamento."""
        return self.db.query(Medidor).join(
            Localidad, Medidor.id_loc == Localidad.id_loc
        ).join(
            Municipio, Localidad.id_mun == Municipio.id_mun
        ).join(
            Departamento, Municipio.id_dep == Departamento.id_dep
        ).filter(
            Departamento.departamento.ilike(f"%{departamento_name}%")
        ).options(
            joinedload(Medidor.localidad).joinedload(Localidad.municipio).joinedload(Municipio.departamento)
        ).all()
    
    def search_medidores(self, search_term: str) -> List[Medidor]:
        """
        Búsqueda flexible de medidores por:
        - Device ID
        - Descripción
        - Localidad
        - Municipio
        - Departamento
        """
        return self.db.query(Medidor).join(
            Localidad, Medidor.id_loc == Localidad.id_loc, isouter=True
        ).join(
            Municipio, Localidad.id_mun == Municipio.id_mun, isouter=True
        ).join(
            Departamento, Municipio.id_dep == Departamento.id_dep, isouter=True
        ).filter(
            (Medidor.deviceid.ilike(f"%{search_term}%")) |
            (Medidor.description.ilike(f"%{search_term}%")) |
            (Localidad.localidad.ilike(f"%{search_term}%")) |
            (Municipio.municipio.ilike(f"%{search_term}%")) |
            (Departamento.departamento.ilike(f"%{search_term}%"))
        ).options(
            joinedload(Medidor.localidad).joinedload(Localidad.municipio).joinedload(Municipio.departamento)
        ).all()

    def get_max_power_in_period(self, device_id: str, start_date: str, end_date: str):
        """
        Obtiene la máxima potencia (kW) en un periodo específico.
        La potencia se calcula como: kwhd / 0.25 (asumiendo lecturas cada 15 minutos)
        """
        try:
            # Convertir fechas a objetos datetime si son strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Ajustar fechas para incluir todo el rango con horas
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            print(f"[DEBUG] Buscando potencia máxima para device_id='{device_id}' desde {start_date} hasta {end_date}")
            
            # Consulta para obtener el máximo valor de kwhd en el periodo
            max_kwhd = self.db.query(func.max(MLectura.kwhd)).filter(
                MLectura.deviceid == device_id,
                MLectura.fecha >= start_date,
                MLectura.fecha <= end_date
            ).scalar()
            
            if max_kwhd is None:
                return None
            
            # Calcular potencia máxima (kW) = kwhd / 0.25
            max_power_kw = max_kwhd / 0.25
            
            # Obtener también la fecha y hora del máximo
            max_record = self.db.query(MLectura).filter(
                MLectura.deviceid == device_id,
                MLectura.fecha >= start_date,
                MLectura.fecha <= end_date,
                MLectura.kwhd == max_kwhd
            ).first()
            
            return {
                'device_id': device_id,
                'max_power_kw': max_power_kw,
                'max_kwhd': max_kwhd,
                'datetime': max_record.fecha if max_record else None,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            print(f"Error en get_max_power_in_period: {e}")
            return None

    def get_total_energy_in_period(self, device_id: str, start_date: str, end_date: str):
        """
        Obtiene la energía total (kWh) consumida en un periodo específico.
        La energía se calcula como la suma de todos los valores kwhd en el periodo.
        """
        try:
            # Convertir fechas a objetos datetime si son strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Ajustar fechas para incluir todo el rango con horas
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            print(f"[DEBUG] Buscando energía para device_id='{device_id}' desde {start_date} hasta {end_date}")
            
            # Consulta para obtener la suma total de kwhd en el periodo
            total_energy = self.db.query(func.sum(MLectura.kwhd)).filter(
                MLectura.deviceid == device_id,
                MLectura.fecha >= start_date,
                MLectura.fecha <= end_date
            ).scalar()
            
            print(f"[DEBUG] Total energy encontrado: {total_energy}")
            
            if total_energy is None:
                return None
            
            # Obtener también el conteo de lecturas
            reading_count = self.db.query(func.count(MLectura.kwhd)).filter(
                MLectura.deviceid == device_id,
                MLectura.fecha >= start_date,
                MLectura.fecha <= end_date
            ).scalar()
            
            # Calcular promedio si hay lecturas
            avg_power_kw = (total_energy / 0.25 / reading_count) if reading_count > 0 else 0
            
            return {
                'device_id': device_id,
                'total_energy_kwh': total_energy,
                'reading_count': reading_count,
                'average_power_kw': avg_power_kw,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'period_days': (end_date.date() - start_date.date()).days + 1
            }
            
        except Exception as e:
            print(f"Error en get_total_energy_in_period: {e}")
            return None