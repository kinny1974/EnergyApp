import pandas as pd
import json
from google import genai

from app.data.repositories import EnergyRepository
from app.data.models import MLectura, Medidor
from app.services.observers import Subject, AuditLoggerObserver, CriticalAlertObserver

class EnergyService(Subject):
    def find_outlier_devices(self, base_year: int, start_date: str, end_date: str, threshold: float):
        """
        Busca medidores con desviaciones mayores al umbral en el rango de fechas dado, usando el año base.
        Devuelve una lista de dicts con device_id, fecha, desviación máxima, curva de carga diaria.
        """
        from datetime import datetime, timedelta
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        medidores = self.repo.get_active_medidores()
        resultados = []
        dias = pd.date_range(start, end, freq='D')
        for medidor in medidores:
            for dia in dias:
                # Obtener lecturas reales del día
                data_orm = self.repo.get_readings_by_date(medidor.deviceid, dia)
                if not data_orm:
                    continue
                df_real = pd.DataFrame([{'time_str': d.fecha.strftime('%H:%M'), 'value': d.kwhd} for d in data_orm])
                # Obtener baseline del año base
                hist_orm = self.repo.get_historical_year_data(medidor.deviceid, base_year)
                if not hist_orm:
                    continue
                df_hist = pd.DataFrame([{'timestamp': d.fecha, 'val': d.kwhd} for d in hist_orm])
                target_day_name = dia.day_name()
                baseline_day = self._calculate_baseline(df_hist, target_day_name)
                if baseline_day.empty:
                    continue
                merged = pd.merge(df_real, baseline_day[['time_str', 'mean', 'std']], on='time_str', how='inner')
                if merged.empty or 'mean' not in merged.columns:
                    continue
                # Calcular desviaciones
                merged['percentage_diff'] = merged.apply(lambda row: ((row['value'] - row['mean']) / row['mean']) * 100 if row['mean'] != 0 else float('inf'), axis=1)
                max_dev = merged['percentage_diff'].abs().max()
                if max_dev >= threshold:
                    resultados.append({
                        'device_id': medidor.deviceid,
                        'fecha': dia.strftime('%Y-%m-%d'),
                        'max_deviation': max_dev,
                        'chart_data': merged.to_dict(orient='records'),
                        'medidor_info': {
                            'description': medidor.description,
                            'devicetype': medidor.devicetype,
                            'customerid': medidor.customerid,
                            'usergroup': medidor.usergroup
                        }
                    })
        return resultados
    def __init__(self, repository: EnergyRepository):
        super().__init__()
        self.repo = repository
        # Adjuntar observadores (Patrón Observer)
        self.attach(AuditLoggerObserver())
        self.attach(CriticalAlertObserver())

    def process_csv_upload(self, df: pd.DataFrame, device_id: str):
        """
        [OMITIDO TEMPORALMENTE]
        Este método está deshabilitado temporalmente para omitir el procesamiento de archivos CSV.
        Concéntrate en los datos obtenidos desde la base de datos.
        """
        # self.validate_device(device_id)
        # readings = []
        # required_columns = ['timestamp', 'value']
        # df.columns = [c.lower().strip() for c in df.columns]
        # for col in required_columns:
        #     if col not in df.columns:
        #         raise ValueError(f"Columna requerida '{col}' no encontrada en el CSV")
        # for _, row in df.iterrows():
        #     try:
        #         fecha = pd.to_datetime(row['timestamp'])
        #         kvar = row.get('kvarhd', 0.0)
        #         readings.append(MLectura(
        #             fecha=fecha,
        #             deviceid=device_id,
        #             kwhd=float(row['value']),
        #             kvarhd=float(kvar)
        #         ))
        #     except Exception as e:
        #         raise ValueError(f"Error procesando fila: {row.to_dict()}. Error: {e}")
        # self.repo.bulk_insert_readings(readings)
        # return {"status": "success", "records": len(readings)}
        return {"status": "omitted", "records": 0, "msg": "Procesamiento de CSV omitido temporalmente."}

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

    def _get_gemini_analysis(self, device_id: str, medidor: Medidor, target_date_str: str, target_day_name: str, merged_df: pd.DataFrame, calculated_estado_general: str):
        """Consulta a la API de Gemini para el análisis (google-genai moderno)."""
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno.")

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

        El estado general determinado por el sistema es: {calculated_estado_general}. Basado en este estado y los datos, genera un reporte técnico estrictamente en formato JSON con estos campos:
        - resumen: Descripción técnica del comportamiento diario.
        - habitos: Identificación de cambios de patrones (ej. encendido temprano).
        - anomalias: Lista de objetos, cada uno con "periodo" (ej: "14:00-15:00") y "descripcion" del evento.
        - recomendacion: Acción sugerida para operación o mantenimiento.
        - estado_general: Mantén el estado general como "{calculated_estado_general}" en tu respuesta.
        
        IMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional antes o después.
        """

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            response_text = response.text.strip()
            
            # Limpiar la respuesta si tiene markdown o texto extra
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].strip()
            
            # Intentar parsear JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Si falla, buscar el primer objeto JSON en la respuesta
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise ValueError("No se encontró JSON válido en la respuesta")
                    
        except Exception as e:
            print(f"Error consultando Gemini: {str(e)}")
            return {
                "resumen": "No se pudo completar el análisis con IA.",
                "habitos": "N/A",
                "anomalias": [str(e)],
                "recomendacion": "Verificar conectividad o API Key.",
                "estado_general": calculated_estado_general
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

    def _determine_overall_state(self, merged_df: pd.DataFrame) -> str:
        """Determina el estado general (NORMAL, ALERTA, CRITICO) basado en las variaciones."""
        
        # Ensure 'mean' column exists to avoid division by zero or KeyError
        if 'mean' not in merged_df.columns:
            return "DESCONOCIDO" # Or raise an error, depending on desired behavior

        # Calculate percentage difference for each point, handling potential division by zero
        # Replace 0 values in 'mean' with NaN to avoid division by zero, then fill NaNs in percentage_diff
        # For our specific thresholds, we consider significant deviations from 0 baseline as critical or alert
        percentage_diff = []
        for index, row in merged_df.iterrows():
            if row['mean'] != 0:
                percentage_diff.append(((row['value'] - row['mean']) / row['mean']) * 100)
            else:
                # If mean is 0, any non-zero value is a significant deviation
                if row['value'] != 0:
                    # Assign a large dummy value to trigger critical/alert if 'value' is present
                    percentage_diff.append(float('inf'))
                else:
                    percentage_diff.append(0.0) # If both are 0, no difference
        
        merged_df['percentage_diff'] = percentage_diff

        # Define thresholds
        NORMAL_THRESHOLD_MAX = 20
        ALERT_THRESHOLD_LOW = -70
        ALERT_THRESHOLD_HIGH = 70
        CRITICAL_THRESHOLD_LOW = -71
        CRITICAL_THRESHOLD_HIGH = 71

        # Check for critical state first
        if (merged_df['percentage_diff'] < CRITICAL_THRESHOLD_LOW).any() or \
           (merged_df['percentage_diff'] > CRITICAL_THRESHOLD_HIGH).any():
            return "CRITICO"
        
        # Check for alert state
        # The condition needs to be adjusted for the ranges given by the user
        # ALERTA  variaciones entre el -70% y -21% o 21% y 70%
        if (merged_df['percentage_diff'].apply(lambda x: ALERT_THRESHOLD_LOW <= x <= -21.0001)).any() or \
           (merged_df['percentage_diff'].apply(lambda x: 21.0001 <= x <= ALERT_THRESHOLD_HIGH)).any():
            return "ALERTA"
            
        # If not critical or alert, it's normal
        return "NORMAL"

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
        
        calculated_estado_general = self._determine_overall_state(merged)

        analysis = self._get_gemini_analysis(device_id, medidor, target_date_str, target_day_name, merged, calculated_estado_general)

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

        calculated_estado_general = self._determine_overall_state(merged)

        analysis = self._get_gemini_analysis(device_id, medidor, target_date_str, target_day_name, merged, calculated_estado_general)

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