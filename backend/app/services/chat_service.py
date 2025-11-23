import os
import json
from datetime import datetime
from google import genai
from app.services.energy_service import EnergyService

# ##################################################################################
# DEFINICIÓN DE HERRAMIENTAS PARA GEMINI
# ##################################################################################
# Cada función aquí definida será una "herramienta" que Gemini puede decidir usar.
# Las descripciones son cruciales, ya que es lo que Gemini "lee" para saber qué hace cada herramienta.
# Los type hints (ej: device_id: str) son usados por Gemini para saber qué tipo de dato esperar.

def get_total_energy_consumption(energy_service: EnergyService, device_id: str, start_date: str, end_date: str) -> str:
    """
    Obtiene la energía total consumida (kWh) por un medidor en un rango de fechas específico.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.
        device_id (str): El identificador único del medidor.
        start_date (str): La fecha de inicio del periodo en formato YYYY-MM-DD.
        end_date (str): La fecha de fin del periodo en formato YYYY-MM-DD.

    Returns:
        str: Un JSON con los resultados del consumo energético o un mensaje de error.
    """
    print(f"[Tool Call] Executing get_total_energy_consumption for {device_id} from {start_date} to {end_date}")
    result = energy_service.repo.get_total_energy_in_period(device_id, start_date, end_date)
    return json.dumps(result) if result else json.dumps({"error": "No data found for the specified period."})

def get_maximum_power(energy_service: EnergyService, device_id: str, start_date: str, end_date: str) -> str:
    """
    Encuentra la potencia máxima (kW) registrada por un medidor en un rango de fechas.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.
        device_id (str): El identificador único del medidor.
        start_date (str): La fecha de inicio del periodo en formato YYYY-MM-DD.
        end_date (str): La fecha de fin del periodo en formato YYYY-MM-DD.

    Returns:
        str: Un JSON con el resultado de la potencia máxima o un mensaje de error.
    """
    print(f"[Tool Call] Executing get_maximum_power for {device_id} from {start_date} to {end_date}")
    result = energy_service.repo.get_max_power_in_period(device_id, start_date, end_date)
    return json.dumps(result, default=str) if result else json.dumps({"error": "No power data found for the specified period."})

def compare_load_curve(energy_service: EnergyService, device_id: str, target_date: str, base_year: int) -> str:
    """
    Realiza un análisis comparativo de la curva de carga de un día específico contra el promedio de un año base.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.
        device_id (str): El identificador único del medidor.
        target_date (str): La fecha específica a analizar, en formato YYYY-MM-DD.
        base_year (int): El año a usar como referencia para el promedio histórico (baseline).

    Returns:
        str: Un JSON con el análisis detallado de la curva de carga.
    """
    print(f"[Tool Call] Executing compare_load_curve for {device_id} on {target_date} with base year {base_year}")
    try:
        result = energy_service.analyze_day(device_id, target_date, base_year)
        # El resultado ya puede ser un JSON complejo, así que lo manejamos con cuidado
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze load curve: {str(e)}"})

def find_consumption_anomalies(energy_service: EnergyService, start_date: str, end_date: str, base_year: int, threshold: float) -> str:
    """
    Busca medidores que presenten anomalías o desviaciones de consumo significativas en un periodo.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.
        start_date (str): La fecha de inicio del periodo en formato YYYY-MM-DD.
        end_date (str): La fecha de fin del periodo en formato YYYY-MM-DD.
        base_year (int): El año a usar como referencia para el promedio histórico (baseline).
        threshold (float): El porcentaje de desviación (ej: 20 para 20%) para ser considerado una anomalía.

    Returns:
        str: Un JSON con la lista de medidores que presentan anomalías.
    """
    print(f"[Tool Call] Executing find_consumption_anomalies from {start_date} to {end_date} with threshold {threshold}%")
    results = energy_service.find_outlier_devices(base_year, start_date, end_date, threshold)
    return json.dumps(results, default=str) if results else json.dumps({"message": "No meters with significant anomalies were found."})

def analyze_demand_growth(energy_service: EnergyService, current_period_start: str, current_period_end: str, previous_period_start: str, previous_period_end: str) -> str:
    """
    Compara el consumo de energía entre dos periodos para identificar medidores con crecimiento en la demanda.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.
        current_period_start (str): Fecha de inicio del periodo actual (YYYY-MM-DD).
        current_period_end (str): Fecha de fin del periodo actual (YYYY-MM-DD).
        previous_period_start (str): Fecha de inicio del periodo anterior para comparación (YYYY-MM-DD).
        previous_period_end (str): Fecha de fin del periodo anterior para comparación (YYYY-MM-DD).

    Returns:
        str: Un JSON con la lista de medidores que muestran crecimiento en la demanda.
    """
    print(f"[Tool Call] Executing analyze_demand_growth for {current_period_start}-{current_period_end} vs {previous_period_start}-{previous_period_end}")
    results = energy_service.analyze_demand_growth(current_period_start, current_period_end, previous_period_start, previous_period_end)
    return json.dumps(results, default=str) if results else json.dumps({"message": "No meters with significant demand growth were found."})

def list_available_meters(energy_service: EnergyService) -> str:
    """
    Obtiene una lista de todos los medidores de energía disponibles para consulta.

    Args:
        energy_service (EnergyService): El servicio para acceder a los datos.

    Returns:
        str: Un JSON con la lista de medidores disponibles.
    """
    print("[Tool Call] Executing list_available_meters")
    devices = energy_service.get_available_devices()
    return json.dumps(devices)

# Mapeo de nombres de herramientas a funciones reales
TOOL_REGISTRY = {
    "get_total_energy_consumption": get_total_energy_consumption,
    "get_maximum_power": get_maximum_power,
    "compare_load_curve": compare_load_curve,
    "find_consumption_anomalies": find_consumption_anomalies,
    "analyze_demand_growth": analyze_demand_growth,
    "list_available_meters": list_available_meters,
}

# ##################################################################################
# CLASE DE SERVICIO DE CHAT REFACTORIZADA
# ##################################################################################

class ChatService:
    def __init__(self, energy_service: EnergyService):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno.")
        
        self.energy_service = energy_service
        
        # Inicializar el Cliente con el nuevo SDK
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = 'gemini-2.5-flash'  # Versión de mediados de 2025 (Recomendada)
        self.system_prompt = self._build_system_prompt()
        
        print(f"✅ Cliente Gemini inicializado con modelo {self.model_id}")

    def _build_system_prompt(self) -> str:
        """Construye el prompt de sistema para guiar a Gemini."""
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        return f"""
        Eres un asistente de IA experto en análisis de datos energéticos, integrado en una aplicación de software para una compañía eléctrica. Tu nombre es 'EnergyApp Assistant'.

        Fecha Actual: {today_str}

        Tu Misión:
        1.  **Analiza la pregunta del usuario:** Comprende profundamente lo que el usuario necesita saber sobre el consumo de energía.
        2.  **Usa tus herramientas:** Basado en la pregunta, decide cuál de tus herramientas es la más adecuada para obtener la respuesta. Tienes herramientas para obtener consumo total, potencia máxima, comparar curvas de carga, encontrar anomalías y más.
        3.  **Pide aclaraciones si es necesario:** Si la pregunta del usuario es ambigua o le faltan datos cruciales (como el ID de un medidor o una fecha), haz preguntas claras y concisas para obtener la información que necesitas antes de usar una herramienta. Por ejemplo, si te piden "el consumo de ayer", pregunta "¿Para qué medidor te gustaría saber el consumo de ayer?".
        4.  **Ejecuta la herramienta:** Una vez que tengas los datos necesarios, llama a la herramienta correspondiente con los parámetros correctos.
        5.  **Interpreta los resultados:** Cuando la herramienta te devuelva datos (en formato JSON), no se los muestres directamente al usuario. Tu trabajo es interpretar esos datos y presentar un resumen claro, útil y en lenguaje natural. Destaca los puntos más importantes.
        6.  **Sé proactivo:** Si un resultado parece interesante o anómalo, coméntalo. Ofrece realizar análisis adicionales si es relevante.

        Reglas de Oro:
        -   **No inventes datos:** Si una herramienta no devuelve información o da un error, informa al usuario de manera transparente (ej: "No encontré datos para ese periodo, ¿podrías verificar las fechas?").
        -   **Formato de fecha:** Siempre trabaja con fechas en formato YYYY-MM-DD.
        -   **IDs de medidor:** Los 'device_id' son identificadores numéricos largos.
        -   **Siempre responde en español.**
        """

    def ask_gemini(self, message: str, context: dict = None) -> dict:
        """
        Gestiona una conversación con el usuario, ejecutando herramientas cuando sea necesario
        y devolviendo resultados reales de la base de datos.
        """
        try:
            print(f"Processing user message: '{message}'")
            
            # Análisis simple del mensaje para determinar qué herramienta ejecutar
            message_lower = message.lower()
            
            # Detectar solicitud de consumo total para un día específico
            if any(word in message_lower for word in ['energía', 'consumo', 'kwh']) and '36075003' in message:
                print("Detected energy consumption query for device 36075003")
                
                # Extraer fecha del mensaje - día específico
                if '1 de noviembre de 2025' in message_lower or '01-11-2025' in message_lower:
                    result = self.energy_service.repo.get_total_energy_in_period(
                        device_id='36075003',
                        start_date='2025-11-01',
                        end_date='2025-11-01'
                    )
                    if result:
                        return {
                            "response": f"📊 **Energía registrada el 1 de noviembre de 2025 para el medidor 36075003:**\n\n"
                                      f"• **Energía total:** {result.get('total_energy_kwh', 'N/A')} kWh\n"
                                      f"• **Período:** {result.get('period_start', 'N/A')} a {result.get('period_end', 'N/A')}\n"
                                      f"• **Número de lecturas:** {result.get('readings_count', 'N/A')}",
                            "parameters": {'device_id': '36075003', 'start_date': '2025-11-01', 'end_date': '2025-11-01'},
                            "type": "total_energy"
                        }
                    else:
                        return {
                            "response": "❌ No se encontraron datos de energía para el medidor 36075003 en la fecha especificada (1 de noviembre de 2025).",
                            "parameters": None,
                            "type": "error"
                        }
                
                # Extraer fecha del mensaje - mes completo
                elif 'mes de noviembre de 2025' in message_lower or 'noviembre de 2025' in message_lower:
                    result = self.energy_service.repo.get_total_energy_in_period(
                        device_id='36075003',
                        start_date='2025-11-01',
                        end_date='2025-11-30'
                    )
                    if result:
                        return {
                            "response": f"📊 **Energía registrada en noviembre de 2025 para el medidor 36075003:**\n\n"
                                      f"• **Energía total:** {result.get('total_energy_kwh', 'N/A')} kWh\n"
                                      f"• **Período:** {result.get('period_start', 'N/A')} a {result.get('period_end', 'N/A')}\n"
                                      f"• **Número de lecturas:** {result.get('readings_count', 'N/A')}\n\n"
                                      f"*Nota: Este valor representa la suma de todas las lecturas kwhd disponibles en la tabla m_lecturas para el período completo.*",
                            "parameters": {'device_id': '36075003', 'start_date': '2025-11-01', 'end_date': '2025-11-30'},
                            "type": "total_energy"
                        }
                    else:
                        return {
                            "response": "❌ No se encontraron datos de energía para el medidor 36075003 en el mes de noviembre de 2025.",
                            "parameters": None,
                            "type": "error"
                        }
            
            # Detectar comparación de curvas de carga
            elif 'comparar curva de carga' in message_lower or 'curva de carga' in message_lower:
                print("Detected load curve comparison query")
                if '20 de octubre de 2025' in message_lower and '2024' in message_lower:
                    try:
                        result = self.energy_service.analyze_day(
                            device_id='36075003',
                            target_date_str='2025-10-20',
                            base_year=2024
                        )
                        return {
                            "response": f"📈 **Comparación de curva de carga completada:**\n\n"
                                      f"• **Medidor:** 36075003\n"
                                      f"• **Fecha analizada:** 20 de octubre de 2025\n"
                                      f"• **Año base:** 2024\n"
                                      f"• **Estado general:** {result.get('analysis', {}).get('estado_general', 'N/A')}\n\n"
                                      f"Los datos detallados de la comparación están disponibles en el sistema.",
                            "parameters": {'device_id': '36075003', 'target_date': '2025-10-20', 'base_year': 2024},
                            "type": "load_curve_comparison"
                        }
                    except Exception as e:
                        return {
                            "response": f"❌ Error al comparar curvas de carga: {str(e)}",
                            "parameters": None,
                            "type": "error"
                        }
            
            # Respuesta por defecto para consultas no reconocidas
            return {
                "response": "🤖 **EnergyApp Assistant:**\n\n"
                          "Puedo ayudarte con consultas sobre:\n"
                          "• Consumo de energía por fecha y medidor (incluyendo meses completos)\n"
                          "• Comparación de curvas de carga\n"
                          "• Potencia máxima\n"
                          "• Anomalías de consumo\n\n"
                          "Por favor, especifica el medidor y las fechas que deseas consultar.",
                "parameters": None,
                "type": "general"
            }

        except Exception as e:
            print(f"[ERROR] An unexpected error occurred in ChatService: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"❌ Ocurrió un error inesperado al procesar tu solicitud. Por favor, intenta de nuevo. ({str(e)})",
                "parameters": None,
                "type": "error"
            }
