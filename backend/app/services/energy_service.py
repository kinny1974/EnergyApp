import pandas as pd
import json
import google.genai as genai
from google.genai import types

from app.data.repositories import EnergyRepository
from app.data.models import MLectura, Medidor
from app.services.observers import Subject, AuditLoggerObserver, CriticalAlertObserver

class EnergyService(Subject):
    def __init__(self, repository: EnergyRepository):
        super().__init__()
        self.repo = repository
        # Adjuntar observadores (Patrón Observer)
        self.attach(AuditLoggerObserver())
        self.attach(CriticalAlertObserver())

    def process_csv_upload(self, df: pd.DataFrame, device_id: str):
        """Transforma DataFrame a Modelos ORM y guarda en base de datos."""
        self.validate_device(device_id)
        
        readings = []
        required_columns = ['timestamp', 'value']
        df.columns = [c.lower().strip() for c in df.columns]
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Columna requerida '{col}' no encontrada en el CSV")
        
        for _, row in df.iterrows():
            try:
                fecha = pd.to_datetime(row['timestamp'])
                kvar = row.get('kvarhd', 0.0)
                
                readings.append(MLectura(
                    fecha=fecha,
                    deviceid=device_id,
                    kwhd=float(row['value']),
                    kvarhd=float(kvar)
                ))
            except Exception as e:
                raise ValueError(f"Error procesando fila: {row.to_dict()}. Error: {e}")
        
        self.repo.bulk_insert_readings(readings)
        return {"status": "success", "records": len(readings)}

    def validate_device(self, device_id: str) -> Medidor:
        """Valida que el dispositivo exista en la tabla medidor."""
        medidor = self.repo.get_medidor(device_id)
        if not medidor:
            raise ValueError(f"Dispositivo {device_id} no encontrado en la tabla medidor")
        return medidor

    def get_years_from_dataframe(self, df: pd.DataFrame):
        """Extrae los años únicos de un DataFrame a partir de la columna 'timestamp'."""
        df.columns = [c.lower().strip() for c in df.columns]
        if 'timestamp' not in df.columns:
            raise ValueError("Columna 'timestamp' no encontrada en el archivo.")
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        years = df['timestamp'].dt.year.unique().tolist()
        return {"years": sorted(years)}

    def _calculate_baseline(self, df_hist: pd.DataFrame, target_day_name: str):
        """Calcula la curva base a partir de un DataFrame histórico."""
        df_hist['ts'] = pd.to_datetime(df_hist['timestamp'])
        df_hist['day_name'] = df_hist['ts'].dt.day_name()
        df_hist['time_str'] = df_hist['ts'].dt.strftime('%H:%M')
        
        if 'value' in df_hist.columns and 'val' not in df_hist.columns:
            df_hist.rename(columns={'value': 'val'}, inplace=True)

        baseline = df_hist.groupby(['day_name', 'time_str'])['val'].agg(['mean', 'std']).reset_index()
        return baseline[baseline['day_name'] == target_day_name].copy()

    def _get_gemini_analysis(self, device_id: str, medidor: Medidor, target_date_str: str, target_day_name: str, merged_df: pd.DataFrame):
        """Consulta a la API de Gemini para el análisis."""
        try:
            client = genai.Client(api_key="AIzaSyA1ZyByyC7m8rl-ImTsvQuwWEobskRvNyY")
            
            sample_data = merged_df.set_index('time_str')[['value', 'mean']].to_string()

            prompt = f"""
            Actúa como un ingeniero electricista experto en demanda energética.
            Analiza el consumo del dispositivo: {device_id} ({medidor.description}) en la fecha: {target_date_str} ({target_day_name}).
            Los valores de 'value' y 'mean' representan energía activa en kWh. Al construir la curva de carga diaria, esto equivale a un valor estimado de la carga en kW.

            Información del medidor:
            - Tipo: {medidor.devicetype}
            - Descripción: {medidor.description}
            - Cliente: {medidor.customerid}
            - Grupo: {medidor.usergroup}

            Datos (Comparativa Consumo Real 'value' vs Esperado 'mean'):
            {sample_data}

            Genera un reporte técnico estrictamente en formato JSON con estos campos:
            - resumen: Descripción técnica del comportamiento diario.
            - habitos: Identificación de cambios de patrones (ej. encendido temprano).
            - anomalias: Lista de objetos, cada uno con "periodo" (ej: "14:00-15:00") y "descripcion" del evento.
            - recomendacion: Acción sugerida para operación o mantenimiento.
            - estado_general: Clasificar solo como "NORMAL", "ALERTA" o "CRITICO".
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.4,
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error consultando Gemini: {str(e)}")
            return {
                "resumen": "No se pudo completar el análisis con IA.",
                "habitos": "N/A",
                "anomalias": [str(e)],
                "recomendacion": "Verificar conectividad o API Key.",
                "estado_general": "DESCONOCIDO"
            }

    def _build_analysis_payload(self, device_id: str, medidor: Medidor, target_day_name: str, merged_df: pd.DataFrame, analysis: dict):
        """Construye el diccionario de respuesta final."""
        payload = {
            "device_id": device_id,
            "medidor_info": {
                "description": medidor.description,
                "devicetype": medidor.devicetype,
                "customerid": medidor.customerid,
                "usergroup": medidor.usergroup
            },
            "day_name": target_day_name,
            "chart_data": merged_df.to_dict(orient='records'),
            "analysis": analysis
        }
        self.notify("ANALYSIS_DONE", payload)
        return payload

    def analyze_day(self, device_id: str, target_date_str: str, base_year: int):
        """Análisis usando datos históricos de la base de datos."""
        target_date = pd.to_datetime(target_date_str)
        medidor = self.validate_device(device_id)
        
        data_orm = self.repo.get_readings_by_date(device_id, target_date)
        if not data_orm:
            raise ValueError(f"No hay datos para {target_date_str} (ID: {device_id})")
        
        df_real = pd.DataFrame([{'time_str': d.fecha.strftime('%H:%M'), 'value': d.kwhd} for d in data_orm])

        hist_orm = self.repo.get_historical_year_data(device_id, base_year)
        if not hist_orm:
            raise ValueError(f"No hay datos históricos del año base {base_year}")
            
        df_hist = pd.DataFrame([{'timestamp': d.fecha, 'val': d.kwhd} for d in hist_orm])
        
        target_day_name = target_date.day_name()
        baseline_day = self._calculate_baseline(df_hist, target_day_name)

        merged = pd.merge(df_real, baseline_day[['time_str', 'mean', 'std']], on='time_str', how='inner')
        
        analysis = self._get_gemini_analysis(device_id, medidor, target_date_str, target_day_name, merged)

        return self._build_analysis_payload(device_id, medidor, target_day_name, merged, analysis)

    def analyze_day_with_df(self, device_id: str, target_date_str: str, base_year: int, base_df: pd.DataFrame):
        """Análisis usando un DataFrame como histórico."""
        target_date = pd.to_datetime(target_date_str)
        medidor = self.validate_device(device_id)

        data_orm = self.repo.get_readings_by_date(device_id, target_date)
        if not data_orm:
            raise ValueError(f"No hay datos para {target_date_str} (ID: {device_id})")
        
        df_real = pd.DataFrame([{'time_str': d.fecha.strftime('%H:%M'), 'value': d.kwhd} for d in data_orm])

        base_df.columns = [c.lower().strip() for c in base_df.columns]
        base_df['timestamp'] = pd.to_datetime(base_df['timestamp'])
        df_hist = base_df[base_df['timestamp'].dt.year == base_year].copy()
        
        if df_hist.empty:
            raise ValueError(f"No hay datos para el año base {base_year} en el archivo proporcionado.")

        target_day_name = target_date.day_name()
        baseline_day = self._calculate_baseline(df_hist, target_day_name)

        merged = pd.merge(df_real, baseline_day[['time_str', 'mean', 'std']], on='time_str', how='inner')

        analysis = self._get_gemini_analysis(device_id, medidor, target_date_str, target_day_name, merged)

        return self._build_analysis_payload(device_id, medidor, target_day_name, merged, analysis)

    def get_available_devices(self):
        """Obtiene lista de medidores disponibles."""
        medidores = self.repo.get_active_medidores()
        return [
            {
                "deviceid": m.deviceid,
                "description": m.description,
                "devicetype": m.devicetype,
                "customerid": m.customerid,
                "usergroup": m.usergroup
            }
            for m in medidores
        ]