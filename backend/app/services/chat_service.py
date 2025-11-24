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

    def _parse_month_year(self, message_lower: str) -> tuple:
        """
        Parsea meses y años en español usando regex.
        Retorna (mes_num, año) o (None, None) si no se encuentra.
        """
        import re
        
        # Mapeo de meses en español
        months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        # Buscar patrón "mes año" o "mes de año"
        for month_name, month_num in months.items():
            pattern = rf'{month_name}\s+(?:de\s+)?(\d{{4}})'
            match = re.search(pattern, message_lower)
            if match:
                year = int(match.group(1))
                return (month_num, year)
        
        return (None, None)
    
    def _extract_device_id(self, message: str) -> str:
        """
        Extrae el device_id del mensaje usando regex.
        """
        import re
        # Buscar números de 8 dígitos (típico para device_id)
        match = re.search(r'\b\d{8}\b', message)
        if match:
            return match.group(0)
        return None
    
    def _determine_query_type(self, message_lower: str) -> str:
        """
        Determina el tipo de consulta basado en palabras clave.
        """
        if any(word in message_lower for word in ['curva de carga', 'comparar curva', 'compara la curva', 'análisis de curva', 'comparación de curva']):
            return 'load_curve_comparison'
        elif any(word in message_lower for word in ['energía', 'consumo', 'kwh', 'consumió']):
            return 'energy_consumption'
        elif any(word in message_lower for word in ['potencia máxima', 'potencia maxima', 'máxima potencia']):
            return 'max_power'
        elif any(word in message_lower for word in ['anomalía', 'anomalia', 'desviación', 'desviacion']):
            return 'anomalies'
        else:
            return 'other'

    def _analyze_query_with_gemini(self, message: str) -> dict:
        """
        Usa Gemini para analizar la consulta del usuario y extraer la información relevante.
        Si Gemini falla, usa un fallback con parsing local.
        """
        analysis_prompt = f"""
        Analiza esta consulta del usuario sobre datos energéticos: "{message}"
        
        Extrae la siguiente información y responde ÚNICAMENTE en formato JSON:
        {{
            "query_type": "energy_consumption" | "max_power" | "load_curve_comparison" | "anomalies" | "other",
            "device_id": "ID del medidor si se menciona, sino null",
            "start_date": "fecha de inicio en formato YYYY-MM-DD si se puede determinar, sino null",
            "end_date": "fecha de fin en formato YYYY-MM-DD si se puede determinar, sino null", 
            "period_description": "descripción del período mencionado (ej: 'agosto 2024', 'último mes')",
            "additional_params": {{"cualquier otro parámetro relevante como año base, umbrales, etc."}}
        }}
        
        Reglas:
        - Si se menciona un mes y año (ej: "agosto 2024"), calcula las fechas de inicio y fin del mes
        - Si se menciona "último lunes", "primer martes", etc., trata de calcular la fecha específica
        - Si no hay suficiente información, devuelve null en los campos correspondientes
        - Los meses en español deben convertirse a números: enero=01, febrero=02, marzo=03, abril=04, mayo=05, junio=06, julio=07, agosto=08, septiembre=09, octubre=10, noviembre=11, diciembre=12
        - Para comparaciones de curva de carga, identifica el query_type como "load_curve_comparison" y extrae:
          * start_date: fecha específica del día a analizar (no un rango)
          * additional_params.base_year: año base para la comparación promedio
        
        Ejemplos:
        - "¿Cuánta energía consumió el medidor 36075003 en agosto 2024?" → query_type: "energy_consumption", start_date: "2024-08-01", end_date: "2024-08-31"
        - "Consumo del medidor 123 el 15 de marzo de 2025" → query_type: "energy_consumption", start_date: "2025-03-15", end_date: "2025-03-15"
        - "Compara la curva de carga del 20 de octubre de 2025 con el promedio de 2024 para el medidor 36075003" → query_type: "load_curve_comparison", device_id: "36075003", start_date: "2025-10-20", additional_params: {{"base_year": 2024}}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=analysis_prompt
            )
            
            response_text = response.text.strip()
            
            # Limpiar la respuesta si tiene markdown
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].strip()
            
            # Parsear JSON
            import json
            analysis = json.loads(response_text)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing query with Gemini: {e}")
            print("Using local fallback parser...")
            
            # FALLBACK: Usar parsing local si Gemini falla
            message_lower = message.lower()
            
            # Extraer device_id
            device_id = self._extract_device_id(message)
            
            # Determinar tipo de consulta
            query_type = self._determine_query_type(message_lower)
            
            # Inicializar variables
            start_date = None
            end_date = None
            period_description = None
            additional_params = {}
            
            # Lógica específica por tipo de consulta
            if query_type == 'load_curve_comparison':
                # Para curvas de carga, buscar fecha específica y año base
                import re
                from datetime import datetime
                
                # Buscar fecha específica (ej: "20 de octubre de 2025", "2025-10-20")
                # Patrón: DD de MES de AAAA
                months_map = {
                    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                }
                
                date_pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
                date_match = re.search(date_pattern, message_lower)
                
                if date_match:
                    day = int(date_match.group(1))
                    month_name = date_match.group(2)
                    year = int(date_match.group(3))
                    
                    if month_name in months_map:
                        month = months_map[month_name]
                        start_date = f"{year}-{month:02d}-{day:02d}"
                        period_description = f"{day} de {month_name} de {year}"
                
                # Buscar año base (ej: "año 2024", "promedio 2024", "año base 2024")
                base_year_pattern = r'(?:año\s+base\s+|promedio\s+(?:del\s+)?año\s+|año\s+)?(\d{4})'
                base_year_matches = re.findall(base_year_pattern, message_lower)
                
                if base_year_matches:
                    # Si hay múltiples años, el último suele ser el año base
                    for year_str in base_year_matches:
                        year_int = int(year_str)
                        # El año base suele ser diferente al año de la fecha analizada
                        if start_date and year_str not in start_date:
                            additional_params['base_year'] = year_int
                            break
                    
                    # Si no encontramos un año diferente, usar el último
                    if 'base_year' not in additional_params and base_year_matches:
                        additional_params['base_year'] = int(base_year_matches[-1])
            
            else:
                # Para otros tipos de consulta, parsear mes y año normalmente
                month_num, year = self._parse_month_year(message_lower)
                
                if month_num and year:
                    # Calcular inicio y fin del mes
                    from calendar import monthrange
                    last_day = monthrange(year, month_num)[1]
                    start_date = f"{year}-{month_num:02d}-01"
                    end_date = f"{year}-{month_num:02d}-{last_day:02d}"
                    
                    # Obtener nombre del mes para la descripción
                    months_names = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                                  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                    period_description = f"{months_names[month_num]} {year}"
            
            return {
                "query_type": query_type,
                "device_id": device_id,
                "start_date": start_date,
                "end_date": end_date,
                "period_description": period_description,
                "additional_params": additional_params
            }

    def _execute_energy_consumption_query(self, device_id: str, start_date: str, end_date: str, period_description: str = None) -> dict:
        """
        Ejecuta una consulta de consumo de energía y formatea la respuesta.
        """
        try:
            result = self.energy_service.repo.get_total_energy_in_period(
                device_id=device_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if result:
                # Determinar si es un día o un período
                is_single_day = start_date == end_date
                period_text = period_description or f"{start_date} a {end_date}"
                
                if is_single_day:
                    title = f"📊 **Energía registrada el {start_date} para el medidor {device_id}:**"
                else:
                    title = f"📊 **Energía registrada en {period_text} para el medidor {device_id}:**"
                
                return {
                    "response": f"{title}\n\n"
                              f"• **Energía total:** {result.get('total_energy_kwh', 'N/A')} kWh\n"
                              f"• **Período:** {result.get('start_date', 'N/A')} a {result.get('end_date', 'N/A')}\n"
                              f"• **Número de lecturas:** {result.get('reading_count', 'N/A')}\n"
                              f"• **Potencia promedio:** {result.get('average_power_kw', 'N/A'):.2f} kW\n"
                              f"• **Días del período:** {result.get('period_days', 'N/A')}\n\n"
                              f"*Nota: Este valor representa la suma de todas las lecturas kwhd disponibles en la base de datos para el período especificado.*",
                    "parameters": {
                        'device_id': device_id, 
                        'start_date': start_date, 
                        'end_date': end_date,
                        'period_description': period_description
                    },
                    "type": "total_energy"
                }
            else:
                return {
                    "response": f"❌ No se encontraron datos de energía para el medidor {device_id} en el período {period_description or f'{start_date} a {end_date}'}.",
                    "parameters": None,
                    "type": "error"
                }
                
        except Exception as e:
            return {
                "response": f"❌ Error al consultar los datos de energía: {str(e)}",
                "parameters": None,
                "type": "error"
            }

    def ask_gemini(self, message: str, context: dict = None) -> dict:
        """
        Gestiona una conversación con el usuario usando Gemini para analizar consultas de manera inteligente.
        """
        try:
            print(f"Processing user message: '{message}'")
            
            # Usar Gemini para analizar la consulta del usuario
            analysis = self._analyze_query_with_gemini(message)
            print(f"Query analysis: {analysis}")
            
            # Ejecutar la acción basada en el análisis
            if analysis.get("query_type") == "energy_consumption":
                device_id = analysis.get("device_id")
                start_date = analysis.get("start_date")
                end_date = analysis.get("end_date")
                period_description = analysis.get("period_description")
                
                if device_id and start_date and end_date:
                    return self._execute_energy_consumption_query(device_id, start_date, end_date, period_description)
                else:
                    # Pedir aclaración si falta información
                    missing_info = []
                    if not device_id:
                        missing_info.append("el ID del medidor")
                    if not start_date or not end_date:
                        missing_info.append("las fechas específicas")
                    
                    return {
                        "response": f"🤖 **EnergyApp Assistant:**\n\n"
                                  f"Para consultar el consumo de energía, necesito que especifiques {' y '.join(missing_info)}.\n\n"
                                  f"Por ejemplo: '¿Cuánta energía consumió el medidor 36075003 en agosto 2024?'",
                        "parameters": analysis,
                        "type": "clarification_needed"
                    }
            
            elif analysis.get("query_type") == "max_power":
                # Lógica para potencia máxima
                device_id = analysis.get("device_id")
                start_date = analysis.get("start_date")
                end_date = analysis.get("end_date")
                
                if device_id and start_date and end_date:
                    try:
                        result = self.energy_service.repo.get_max_power_in_period(device_id, start_date, end_date)
                        if result:
                            return {
                                "response": f"⚡ **Potencia máxima para el medidor {device_id}:**\n\n"
                                          f"• **Potencia máxima:** {result.get('max_power_kw', 'N/A'):.2f} kW\n"
                                          f"• **Fecha y hora:** {result.get('datetime', 'N/A')}\n"
                                          f"• **Período analizado:** {result.get('start_date', 'N/A')} a {result.get('end_date', 'N/A')}",
                                "parameters": analysis,
                                "type": "max_power"
                            }
                        else:
                            return {
                                "response": f"❌ No se encontraron datos de potencia para el medidor {device_id} en el período especificado.",
                                "parameters": None,
                                "type": "error"
                            }
                    except Exception as e:
                        return {
                            "response": f"❌ Error al consultar la potencia máxima: {str(e)}",
                            "parameters": None,
                            "type": "error"
                        }
                else:
                    return {
                        "response": "🤖 **EnergyApp Assistant:**\n\nPara consultar la potencia máxima, necesito el ID del medidor y las fechas específicas.",
                        "parameters": analysis,
                        "type": "clarification_needed"
                    }
            
            elif analysis.get("query_type") == "load_curve_comparison":
                # Lógica para comparación de curvas de carga
                device_id = analysis.get("device_id")
                target_date = analysis.get("start_date")  # Fecha específica a analizar
                base_year = analysis.get("additional_params", {}).get("base_year")
                
                # Si no hay base_year en additional_params, buscar en el mensaje
                if not base_year:
                    import re
                    # Buscar año base mencionado (ej: "año 2024", "año base 2024", "promedio 2024")
                    match = re.search(r'(?:año\s+base\s+|promedio\s+|año\s+)?(\d{4})', message.lower())
                    if match:
                        base_year = int(match.group(1))
                
                if device_id and target_date and base_year:
                    try:
                        result = self.energy_service.analyze_day(
                            device_id=device_id,
                            target_date_str=target_date,
                            base_year=base_year
                        )
                        
                        # Extraer información clave del análisis
                        estado = result.get('analysis', {}).get('estado_general', 'N/A')
                        resumen = result.get('analysis', {}).get('resumen', 'Análisis completado')
                        anomalias = result.get('analysis', {}).get('anomalias', [])
                        recomendacion = result.get('analysis', {}).get('recomendacion', 'N/A')
                        
                        # Formatear anomalías
                        anomalias_text = ""
                        if anomalias and isinstance(anomalias, list):
                            anomalias_text = "\n\n**🔍 Anomalías detectadas:**\n"
                            for i, anomalia in enumerate(anomalias, 1):
                                if isinstance(anomalia, dict):
                                    periodo = anomalia.get('periodo', 'N/A')
                                    descripcion = anomalia.get('descripcion', 'N/A')
                                    anomalias_text += f"{i}. **{periodo}:** {descripcion}\n"
                                else:
                                    anomalias_text += f"{i}. {anomalia}\n"
                        elif not anomalias:
                            anomalias_text = "\n\n**✅ No se detectaron anomalías significativas.**"
                        
                        return {
                            "response": f"📈 **Comparación de curva de carga completada**\n\n"
                                      f"• **Medidor:** {device_id}\n"
                                      f"• **Fecha analizada:** {target_date}\n"
                                      f"• **Año base (promedio):** {base_year}\n"
                                      f"• **Estado general:** {estado}\n\n"
                                      f"**📊 Resumen del análisis:**\n{resumen}\n"
                                      f"{anomalias_text}\n"
                                      f"**💡 Recomendación:**\n{recomendacion}",
                            "parameters": {
                                'device_id': device_id,
                                'target_date': target_date,
                                'base_year': base_year
                            },
                            "type": "load_curve_comparison",
                            "full_analysis": result
                        }
                    except ValueError as e:
                        return {
                            "response": f"❌ **Error al comparar curvas de carga:** {str(e)}\n\n"
                                      f"Verifica que:\n"
                                      f"• El medidor {device_id} tenga datos para la fecha {target_date}\n"
                                      f"• Existan datos históricos del año base {base_year}",
                            "parameters": None,
                            "type": "error"
                        }
                    except Exception as e:
                        return {
                            "response": f"❌ **Error inesperado al comparar curvas de carga:** {str(e)}",
                            "parameters": None,
                            "type": "error"
                        }
                else:
                    # Pedir aclaración si falta información
                    missing_info = []
                    if not device_id:
                        missing_info.append("el ID del medidor")
                    if not target_date:
                        missing_info.append("la fecha específica a analizar")
                    if not base_year:
                        missing_info.append("el año base para la comparación")
                    
                    return {
                        "response": f"🤖 **EnergyApp Assistant:**\n\n"
                                  f"Para comparar curvas de carga, necesito que especifiques {', '.join(missing_info)}.\n\n"
                                  f"Por ejemplo: 'Compara la curva de carga del 20 de octubre de 2025 con el promedio del año 2024 para el medidor 36075003'",
                        "parameters": analysis,
                        "type": "clarification_needed"
                    }
            
            else:
                # Respuesta por defecto con sugerencias inteligentes
                return {
                    "response": "🤖 **EnergyApp Assistant:**\n\n"
                              "Puedo ayudarte con consultas sobre:\n"
                              "• **Consumo de energía:** 'Energía consumida por el medidor 36075003 en agosto 2024'\n"
                              "• **Potencia máxima:** 'Potencia máxima del medidor 36075003 en septiembre 2024'\n"
                              "• **Comparación de curvas de carga:** 'Comparar curva del 15 de octubre con año base 2023'\n"
                              "• **Anomalías de consumo:** 'Medidores con anomalías en julio 2024'\n\n"
                              "Por favor, especifica el medidor y las fechas que deseas consultar.",
                    "parameters": analysis,
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
