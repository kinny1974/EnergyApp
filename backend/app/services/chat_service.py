import os
import re
from google import genai

class ChatService:
    def __init__(self, energy_service=None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno.")
        self.energy_service = energy_service

    def ask_gemini(self, message: str, context: dict = None) -> str:
        """
        Envía un mensaje a Gemini, agregando contexto eléctrico si se provee.
        Usa un sistema híbrido: primero regex para casos claros, luego Gemini para clasificación.
        """
        try:
            # DEBUG: Agregar logging para ver qué está detectando
            print(f"[DEBUG] Mensaje recibido: {message}")
            
            # Detectar si la pregunta es sobre crecimiento de demanda (primero porque puede contener palabras de otras consultas)
            if self._is_demand_growth_query(message):
                print(f"[DEBUG] Detectado como consulta de crecimiento de demanda (regex)")
                return self._handle_demand_growth_query(message)
            
            # Detectar si la pregunta es sobre búsqueda de outliers/desviaciones
            if self._is_outlier_query(message):
                print(f"[DEBUG] Detectado como consulta de outliers (regex)")
                return self._handle_outlier_query(message)
            
            # Detectar si la pregunta es sobre máxima potencia
            if self._is_max_power_query(message):
                print(f"[DEBUG] Detectado como consulta de máxima potencia (regex)")
                return self._handle_max_power_query(message)
            
            # Detectar si la pregunta es sobre energía total
            if self._is_total_energy_query(message):
                print(f"[DEBUG] Detectado como consulta de energía total (regex)")
                return self._handle_total_energy_query(message)
            
            # Si no se detectó con regex, usar Gemini para clasificar la intención
            print(f"[DEBUG] No detectado por regex, clasificando con Gemini")
            intent = self._classify_intent_with_gemini(message)
            print(f"[DEBUG] Intención clasificada por Gemini: {intent}")
            
            # Procesar según la intención clasificada
            if intent == "demand_growth":
                return self._handle_demand_growth_query(message)
            elif intent == "outlier":
                return self._handle_outlier_query(message)
            elif intent == "max_power":
                return self._handle_max_power_query(message)
            elif intent == "total_energy":
                return self._handle_total_energy_query(message)
            else:
                # Para preguntas generales, usar Gemini normalmente
                prompt = self._build_prompt(message, context)
                
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
        except Exception as e:
            return f"Error consultando Gemini: {str(e)}"

    def _is_outlier_query(self, message: str) -> bool:
        """Detecta si la pregunta es sobre búsqueda de outliers/desviaciones."""
        patterns = [
            r"medidores.*desviaciones.*mayor.*\d+%",
            r"busca.*medidores.*\d+%",
            r"outliers.*medidores",
            r"anomalías.*consumo",
            r"encuentra.*medidores.*exceden"
        ]
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in patterns)

    def _is_max_power_query(self, message: str) -> bool:
        """Detecta si la pregunta es sobre máxima potencia."""
        patterns = [
            r"máxima?\s+potencia",
            r"potencia\s+máxima?",
            r"máximo\s+de\s+potencia",
            r"potencia\s+pico",
            r"pico\s+de\s+potencia",
            r"mayor\s+potencia",
            r"potencia.*máximo",
            r"máximo.*kw"
        ]
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in patterns)

    def _is_total_energy_query(self, message: str) -> bool:
        """Detecta si la pregunta es sobre energía total/consumo/demanda."""
        patterns = [
            r"energía\s+(total|consumida|del\s+periodo)",
            r"(total|suma)\s+de\s+energía",
            r"consumo\s+(total|de\s+energía)",
            r"energía.*entre.*y",
            r"energía.*mes",
            r"energía.*año",
            r"kwh\s+(total|consumidos?)",
            r"suma.*kwh",
            r"consumo.*kwh",
            # Nuevos patrones más específicos
            r"consumo\s+registrado\s+por\s+el\s+medidor",
            r"consumo.*medidor.*\d+",
            r"device_id.*\d+.*consumo",
            r"medidor.*\d+.*consumo",
            r"cuánto\s+(consumió|ha\s+consumido)",
            r"qué\s+(consumo|cantidad).*medidor",
            r"datos\s+de\s+consumo",
            r"lecturas.*medidor",
            r"base_year.*\d{4}",
            # Patrones para "demanda de energía"
            r"demanda\s+(de\s+)?energía",
            r"calcula\s+(la\s+)?demanda",
            r"demanda.*medidor",
            r"demanda.*semana",
            # Patrones para "última semana de [mes]"
            r"última\s+semana\s+(de\s+)?\w+",
            r"semana\s+final\s+(de\s+)?\w+",
            r"calcula.*semana.*\w+"
        ]
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in patterns)

    def _is_demand_growth_query(self, message: str) -> bool:
        """Detecta si la pregunta es sobre crecimiento/comparación de demanda entre periodos."""
        patterns = [
            r"medidores.*mayor\s+crecimiento",
            r"crecimiento\s+de\s+la\s+demanda",
            r"comparación.*demanda.*semana",
            r"comparar.*consumo.*semana",
            r"aumento.*demanda.*semana",
            r"incremento.*consumo.*semana",
            r"evolución.*demanda.*semana",
            r"variación.*demanda.*semana",
            r"cambio.*demanda.*semana",
            r"análisis.*comparativo.*demanda",
            # Patrones más específicos para la consulta del usuario
            r"determinar.*medidores.*mayor\s+crecimiento.*demanda",
            r"primera\s+semana.*noviembre.*comparación.*primera\s+semana.*mes\s+anterior",
            # Patrones más flexibles
            r"mayor\s+crecimiento.*demanda.*primera\s+semana",
            r"crecimiento.*demanda.*semana.*comparación",
            r"comparar.*primera\s+semana",
            r"primera\s+semana.*\w+.*comparación.*primera\s+semana",
            r"medidores.*crecimiento.*semana.*\w+.*mes\s+anterior"
        ]
        message_lower = message.lower()
        is_match = any(re.search(pattern, message_lower) for pattern in patterns)
        print(f"[DEBUG] _is_demand_growth_query: '{message_lower}' -> {is_match}")
        if is_match:
            print(f"[DEBUG] Patrón coincidente encontrado para crecimiento de demanda")
        return is_match

    def _handle_outlier_query(self, message: str) -> str:
        """Procesa consultas sobre búsqueda de outliers usando EnergyService."""
        if not self.energy_service:
            return "Error: No tengo acceso al servicio de análisis energético para buscar datos reales."
        
        try:
            # Extraer parámetros de la consulta usando regex
            params = self._extract_outlier_params(message)
            
            if not all([params['base_year'], params['start_date'], params['end_date'], params['threshold']]):
                return "Error: No pude extraer todos los parámetros necesarios de tu consulta. Por favor, especifica el año base, el periodo de análisis y el porcentaje de desviación."
            
            # Informar que se está procesando
            print(f"Procesando consulta de outliers: {params}")
            
            # Ejecutar búsqueda de outliers con manejo de timeout
            results = self.energy_service.find_outlier_devices(
                base_year=params['base_year'],
                start_date=params['start_date'], 
                end_date=params['end_date'],
                threshold=params['threshold']
            )
            
            if not results:
                return f"✅ **Análisis Completado**\n\nNo se encontraron medidores con desviaciones mayores al {params['threshold']}% en el periodo del {params['start_date']} al {params['end_date']}."
            
            # Formatear respuesta
            return self._format_outlier_response(results, params)
            
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return "❌ **Error de Timeout**\n\nLa consulta tardó demasiado tiempo. Intenta reducir el rango de fechas o contacta al administrador."
            elif "database" in error_msg.lower():
                return "❌ **Error de Base de Datos**\n\nNo se pudo conectar a la base de datos. Verifica que el servicio esté funcionando."
            else:
                return f"❌ **Error procesando la consulta:** {error_msg}"

    def _handle_max_power_query(self, message: str) -> str:
        """Procesa consultas sobre máxima potencia usando EnergyService."""
        if not self.energy_service:
            return "Error: No tengo acceso al servicio de análisis energético para buscar datos reales."
        
        try:
            # Extraer parámetros de la consulta
            params = self._extract_max_power_params(message)
            
            if not all([params['device_id'], params['start_date'], params['end_date']]):
                return "Error: No pude extraer todos los parámetros necesarios. Por favor, especifica el medidor y el periodo (día/mes/año)."
            
            # Obtener datos de máxima potencia
            result = self.energy_service.repo.get_max_power_in_period(
                device_id=str(params['device_id']),  # Asegurar que sea string
                start_date=params['start_date'],
                end_date=params['end_date']
            )
            
            if not result:
                return f"❌ No se encontraron datos de potencia para el medidor {params['device_id']} en el periodo especificado."
            
            return self._format_max_power_response(result, params)
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                return "❌ **Medidor no encontrado:** Verifica que el ID del medidor sea correcto."
            else:
                return f"❌ **Error procesando consulta de potencia:** {error_msg}"

    def _extract_max_power_params(self, message: str):
        """Extrae parámetros de consultas de máxima potencia."""
        params = {
            'device_id': None,
            'start_date': None,
            'end_date': None,
            'period_type': None
        }
        
        # Buscar ID del medidor (patrones como "medidor X", "device X", etc.)
        device_patterns = [
            r"medidor\s+([A-Za-z0-9_-]+)",
            r"device\s+([A-Za-z0-9_-]+)",
            r"dispositivo\s+([A-Za-z0-9_-]+)",
            r"para\s+([A-Za-z0-9_-]+)"
        ]
        
        for pattern in device_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['device_id'] = match.group(1)
                break
        
        # Detectar tipo de periodo
        message_lower = message.lower()
        if "día" in message_lower or "hoy" in message_lower:
            params['period_type'] = 'day'
            # Buscar fecha específica o usar hoy
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
            if date_match:
                date_str = date_match.group(1)
                params['start_date'] = date_str
                params['end_date'] = date_str
            else:
                # Si no hay fecha específica, usar hoy
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                params['start_date'] = today
                params['end_date'] = today
                
        elif "mes" in message_lower:
            params['period_type'] = 'month'
            # Buscar patrón mes/año
            month_match = re.search(r'(\d{4}-\d{2})', message)
            if month_match:
                year_month = month_match.group(1)
                params['start_date'] = f"{year_month}-01"
                # Calcular último día del mes
                from datetime import datetime, timedelta
                try:
                    next_month = datetime.strptime(f"{year_month}-01", "%Y-%m-%d") + timedelta(days=32)
                    last_day = (next_month.replace(day=1) - timedelta(days=1)).day
                    params['end_date'] = f"{year_month}-{last_day:02d}"
                except:
                    params['end_date'] = f"{year_month}-31"
                    
        elif "año" in message_lower:
            params['period_type'] = 'year'
            year_match = re.search(r'(\d{4})', message)
            if year_match:
                year = year_match.group(1)
                params['start_date'] = f"{year}-01-01"
                params['end_date'] = f"{year}-12-31"
        
        return params

    def _format_max_power_response(self, result, params):
        """Formatea la respuesta de máxima potencia de manera más humana y natural."""
        # Construir respuesta más humana
        response = f"¡Listo! He analizado la máxima potencia del medidor **{result['device_id']}**.\n\n"
        
        response += f"📅 **Periodo analizado:** Del {result['start_date']} al {result['end_date']}\n\n"
        
        response += f"**Resultados obtenidos:**\n"
        response += f"• **Potencia máxima registrada:** {result['max_power_kw']:.1f} kW\n"
        response += f"• **Energía en el momento del pico:** {result['max_kwhd']:.3f} kWh\n"
        
        if result['datetime']:
            from datetime import datetime
            fecha_hora = result['datetime']
            if isinstance(fecha_hora, str):
                fecha_hora = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
            
            fecha_natural = fecha_hora.strftime("%d de %B de %Y a las %H:%M")
            response += f"• **Momento del pico:** {fecha_natural}\n\n"
        else:
            response += "\n"
        
        # Agregar contexto interpretativo sobre la potencia
        if result['max_power_kw'] > 100:
            power_context = "Esta es una potencia muy alta, típica de equipos industriales o grandes sistemas de climatización."
        elif result['max_power_kw'] > 50:
            power_context = "Esta potencia corresponde a equipos comerciales medianos o sistemas de bombeo importantes."
        elif result['max_power_kw'] > 10:
            power_context = "Este nivel de potencia es característico de comercios pequeños o residencias con varios equipos funcionando simultáneamente."
        else:
            power_context = "Esta potencia es moderada, similar al consumo de electrodomésticos comunes en una residencia."
        
        response += f"💡 **Interpretación:** {power_context}\n\n"
        
        response += "¿Necesitas que analice algún otro aspecto del consumo energético?"
        
        return response

    def _handle_total_energy_query(self, message: str) -> str:
        """Procesa consultas sobre energía total usando EnergyService."""
        if not self.energy_service:
            return "Error: No tengo acceso al servicio de análisis energético para buscar datos reales."
        
        try:
            # Extraer parámetros de la consulta
            params = self._extract_energy_params(message)
            print(f"[DEBUG] Parámetros extraídos: {params}")
            
            if not all([params['device_id'], params['start_date'], params['end_date']]):
                missing = [k for k, v in params.items() if not v and k in ['device_id', 'start_date', 'end_date']]
                return f"Error: No pude extraer los parámetros: {missing}. Por favor, especifica el medidor y el periodo claramente."
            
            # Obtener datos de energía total
            result = self.energy_service.repo.get_total_energy_in_period(
                device_id=str(params['device_id']),  # Asegurar que sea string
                start_date=params['start_date'],
                end_date=params['end_date']
            )
            
            if not result:
                # Si no encuentra datos en el año actual, buscar en años anteriores
                found_in_other_year = False
                for year_offset in [1, 2, 3]:  # Buscar en los últimos 3 años
                    from datetime import datetime
                    search_year = datetime.now().year - year_offset
                    
                    # Crear nuevo periodo para el año anterior
                    if params['period_type'] == 'month':
                        # Extraer el mes del periodo original
                        month_part = params['start_date'].split('-')[1]
                        test_start = f"{search_year}-{month_part}-01"
                        
                        # Calcular último día del mes
                        from datetime import timedelta
                        try:
                            next_month = datetime.strptime(test_start, "%Y-%m-%d") + timedelta(days=32)
                            last_day = (next_month.replace(day=1) - timedelta(days=1)).day
                            test_end = f"{search_year}-{month_part}-{last_day:02d}"
                        except:
                            test_end = f"{search_year}-{month_part}-31"
                    else:
                        test_start = f"{search_year}-01-01"
                        test_end = f"{search_year}-12-31"
                    
                    # Buscar en este año alternativo
                    result_alt = self.energy_service.repo.get_total_energy_in_period(
                        device_id=str(params['device_id']),  # Asegurar que sea string
                        start_date=test_start,
                        end_date=test_end
                    )
                    
                    if result_alt:
                        found_in_other_year = True
                        return f"✅ **Datos encontrados en {search_year}:**\n\n" + self._format_total_energy_response(result_alt, {'device_id': params['device_id'], 'period_type': params['period_type']}) + f"\n\n💡 **Nota:** No había datos para {params['start_date'][:4]}, se usaron datos de {search_year}."
                
                if not found_in_other_year:
                    # Intentar mostrar medidores disponibles para ayudar al usuario
                    try:
                        available_devices = self.energy_service.get_available_devices()
                        device_list = ", ".join([d['deviceid'] for d in available_devices['devices'][:5]])
                        return f"❌ No se encontraron datos de energía para el medidor {params['device_id']} en el periodo {params['start_date']} a {params['end_date']} ni en años anteriores.\n\n💡 **Medidores disponibles:** {device_list}"
                    except:
                        return f"❌ No se encontraron datos de energía para el medidor {params['device_id']} en el periodo {params['start_date']} a {params['end_date']}.\n\n💡 **Sugerencia:** Verifica que el ID del medidor sea correcto y que haya datos para el periodo solicitado."
            
            return self._format_total_energy_response(result, params)
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                # Intentar mostrar medidores disponibles
                try:
                    available_devices = self.energy_service.get_available_devices()
                    device_list = ", ".join([d['deviceid'] for d in available_devices['devices'][:5]])
                    return f"❌ **Medidor no encontrado:** {params['device_id']}\n\n💡 **Medidores disponibles:** {device_list}\n\n**Sugerencia:** Verifica el ID del medidor."
                except:
                    return "❌ **Medidor no encontrado:** Verifica que el ID del medidor sea correcto."
            else:
                return f"❌ **Error procesando consulta de energía:** {error_msg}"

    def _extract_energy_params(self, message: str):
        """Extrae parámetros de consultas de energía total."""
        params = {
            'device_id': None,
            'start_date': None,
            'end_date': None,
            'period_type': None
        }
        
        # Función auxiliar para detectar meses por nombre
        def detect_month_by_name(text):
            meses = {
                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
            }
            text_lower = text.lower()
            for mes_nombre, mes_numero in meses.items():
                if mes_nombre in text_lower:
                    return mes_numero
            return None
        
        # Función auxiliar para calcular última semana del mes
        def get_last_week_of_month(year: int, month: int):
            """Calcula las fechas de la última semana de un mes (lunes a domingo)."""
            from datetime import datetime, timedelta
            
            # Primer día del mes siguiente
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            
            # Último día del mes actual
            last_day = next_month - timedelta(days=1)
            
            # Encontrar el domingo de la última semana (último día del mes)
            # y retroceder 6 días para obtener el lunes de la última semana
            last_sunday = last_day
            last_monday = last_sunday - timedelta(days=6)
            
            return last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d")
        
        # Buscar ID del medidor (patrones como "medidor X", "device X", etc.)
        device_patterns = [
            r"medidor\s+([A-Za-z0-9_-]+)",
            r"device\s+([A-Za-z0-9_-]+)",
            r"dispositivo\s+([A-Za-z0-9_-]+)",
            r"para\s+([A-Za-z0-9_-]+)",
            r"del\s+([A-Za-z0-9_-]+)",
            # Nuevos patrones específicos
            r"device_id[:\s]+([A-Za-z0-9_-]+)",
            r"id[:\s]+([A-Za-z0-9_-]+)",
            r"\b(\d{7,})\b",  # Números largos como IDs (7+ dígitos)
            r"por\s+el\s+medidor\s+([A-Za-z0-9_-]+)",  # "por el medidor X"
            r"el\s+medidor\s+([A-Za-z0-9_-]+)"  # "el medidor X"
        ]
        
        for pattern in device_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['device_id'] = match.group(1)
                break
        
        # Detectar "última semana de [mes] [año]"
        last_week_match = re.search(r'última\s+semana\s+(?:de\s+)?(\w+)(?:\s+de\s+(\d{4}))?', message, re.IGNORECASE)
        if last_week_match:
            month_name = last_week_match.group(1).lower()
            year_str = last_week_match.group(2)
            
            # Convertir nombre del mes a número
            month_num = detect_month_by_name(month_name)
            if month_num:
                # Determinar año (usar año actual si no se especifica)
                from datetime import datetime
                if year_str:
                    year = int(year_str)
                else:
                    year = datetime.now().year
                
                # Calcular última semana del mes
                start_date, end_date = get_last_week_of_month(year, int(month_num))
                params['start_date'] = start_date
                params['end_date'] = end_date
                params['period_type'] = 'last_week'
                print(f"[DEBUG] Última semana detectada: {month_name} {year} -> {start_date} a {end_date}")
                return params
        
        # Detectar rango de fechas específico "entre X y Y"
        date_range_match = re.search(r'entre\s+(\d{4}-\d{2}-\d{2})\s+y\s+(\d{4}-\d{2}-\d{2})', message)
        if date_range_match:
            params['start_date'] = date_range_match.group(1)
            params['end_date'] = date_range_match.group(2)
            params['period_type'] = 'custom_range'
            return params
        
        # Detectar mes por nombre antes de otras detecciones
        month_detected = detect_month_by_name(message)
        if month_detected:
            params['period_type'] = 'month'
            # Buscar año (por defecto usar año actual si no se especifica)
            year_match = re.search(r'\b(20[012]\d)\b', message)
            if year_match:
                year_found = year_match.group(1)
                print(f"[DEBUG] Año encontrado en mensaje: {year_found}")
            else:
                # Si no hay año específico, usar año actual como fallback
                # La búsqueda inteligente se hará después en _handle_total_energy_query
                from datetime import datetime
                year_found = str(datetime.now().year)
                print(f"[DEBUG] Usando año actual por defecto: {year_found} (se buscará en otros años si no hay datos)")
            
            params['start_date'] = f"{year_found}-{month_detected}-01"
            # Calcular último día del mes
            from datetime import datetime, timedelta
            try:
                next_month = datetime.strptime(f"{year_found}-{month_detected}-01", "%Y-%m-%d") + timedelta(days=32)
                last_day = (next_month.replace(day=1) - timedelta(days=1)).day
                params['end_date'] = f"{year_found}-{month_detected}-{last_day:02d}"
            except:
                params['end_date'] = f"{year_found}-{month_detected}-31"
            
            print(f"[DEBUG] Mes detectado: {month_detected} -> Periodo: {params['start_date']} a {params['end_date']}")
            return params
        
        # Detectar tipo de periodo
        message_lower = message.lower()
        if "día" in message_lower or "hoy" in message_lower:
            params['period_type'] = 'day'
            # Buscar fecha específica o usar hoy
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
            if date_match:
                date_str = date_match.group(1)
                params['start_date'] = date_str
                params['end_date'] = date_str
            else:
                # Si no hay fecha específica, usar hoy
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                params['start_date'] = today
                params['end_date'] = today
                
        elif "mes" in message_lower:
            params['period_type'] = 'month'
            # Buscar patrón mes/año
            month_match = re.search(r'(\d{4}-\d{2})', message)
            if month_match:
                year_month = month_match.group(1)
                params['start_date'] = f"{year_month}-01"
                # Calcular último día del mes
                from datetime import datetime, timedelta
                try:
                    next_month = datetime.strptime(f"{year_month}-01", "%Y-%m-%d") + timedelta(days=32)
                    last_day = (next_month.replace(day=1) - timedelta(days=1)).day
                    params['end_date'] = f"{year_month}-{last_day:02d}"
                except:
                    params['end_date'] = f"{year_month}-31"
                    
        elif "año" in message_lower:
            params['period_type'] = 'year'
            year_match = re.search(r'(\d{4})', message)
            if year_match:
                year = year_match.group(1)
                params['start_date'] = f"{year}-01-01"
                params['end_date'] = f"{year}-12-31"
        
        # Detectar base_year en el mensaje
        base_year_match = re.search(r'base_year[:\s]+(\d{4})', message)
        if base_year_match:
            base_year = base_year_match.group(1)
            # Si hay base_year pero no periodo específico, usar todo el año
            if not params['start_date']:
                params['start_date'] = f"{base_year}-01-01"
                params['end_date'] = f"{base_year}-12-31"
                params['period_type'] = 'base_year'
        
        # Si no se encontró periodo específico, usar un rango por defecto
        if not params['start_date']:
            # Buscar cualquier año mencionado
            year_match = re.search(r'\b(20[012]\d)\b', message)
            if year_match:
                year = year_match.group(1)
                params['start_date'] = f"{year}-01-01"
                params['end_date'] = f"{year}-12-31"
                params['period_type'] = 'year'
            else:
                # Si no hay año específico, usar el año actual
                from datetime import datetime
                current_year = datetime.now().year
                print(f"[DEBUG] Usando año actual por defecto: {current_year}")
                params['start_date'] = f"{current_year}-01-01"
                params['end_date'] = f"{current_year}-12-31"
                params['period_type'] = 'current_year'
        
        return params

    def _format_total_energy_response(self, result, params):
        """Formatea la respuesta de energía total de manera más humana y natural."""
        # Formatear fechas de manera más legible
        start_date = result['start_date']
        end_date = result['end_date']
        period_days = result['period_days']
        
        # Convertir formato de fecha (YYYY-MM-DD) a algo más natural
        def format_date_natural(date_str):
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                     'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            return f"{date_obj.day} de {months[date_obj.month-1]} de {date_obj.year}"
        
        start_natural = format_date_natural(start_date)
        end_natural = format_date_natural(end_date)
        
        # Construir respuesta más humana
        response = f"¡Perfecto! He calculado la demanda de energía para el medidor **{result['device_id']}**.\n\n"
        
        response += f"📅 **Periodo analizado:** Del {start_natural} al {end_natural} "
        response += f"({period_days} días)\n\n"
        
        response += f"**Resultados obtenidos:**\n"
        response += f"• **Energía total consumida:** {result['total_energy_kwh']:,.0f} kWh\n"
        response += f"• **Potencia promedio:** {result['average_power_kw']:.1f} kW\n"
        
        # Calcular estadísticas adicionales con contexto
        daily_avg = result['total_energy_kwh'] / result['period_days']
        response += f"• **Consumo diario promedio:** {daily_avg:,.0f} kWh/día\n"
        response += f"• **Lecturas procesadas:** {result['reading_count']:,} registros\n\n"
        
        # Agregar contexto interpretativo
        if result['total_energy_kwh'] > 10000:
            energy_context = "Este es un consumo bastante elevado, típico de instalaciones industriales o comerciales grandes."
        elif result['total_energy_kwh'] > 5000:
            energy_context = "Este consumo corresponde a una instalación comercial mediana o industrial pequeña."
        elif result['total_energy_kwh'] > 1000:
            energy_context = "Este nivel de consumo es característico de comercios pequeños o residencias con alto consumo."
        else:
            energy_context = "Este es un consumo moderado, similar al de una residencia promedio."
        
        response += f"💡 **Interpretación:** {energy_context}\n\n"
        
        response += "¿Te gustaría que analice algún otro periodo o medidor?"
        
        return response

    def _extract_outlier_params(self, message: str):
        """Extrae parámetros de la consulta de outliers."""
        params = {
            'base_year': None,
            'start_date': None,
            'end_date': None,
            'threshold': None
        }
        
        # Extraer año base
        year_match = re.search(r'año\s+(\d{4})', message)
        if year_match:
            params['base_year'] = int(year_match.group(1))
        
        # Extraer umbral de desviación
        threshold_match = re.search(r'(\d+)%', message)
        if threshold_match:
            params['threshold'] = float(threshold_match.group(1))
        
        # Extraer periodo - buscar patrones como "enero y octubre de 2025"
        period_match = re.search(r'enero.*octubre.*(\d{4})', message, re.IGNORECASE)
        if period_match:
            year = period_match.group(1)
            params['start_date'] = f"{year}-01-01"
            params['end_date'] = f"{year}-10-31"
        else:
            # Buscar otros patrones de fecha
            date_match = re.search(r'(\d{4})', message)
            if date_match:
                year = date_match.group(1)
                params['start_date'] = f"{year}-01-01"
                params['end_date'] = f"{year}-12-31"
        
        return params

    def _format_outlier_response(self, results, params):
        """Formatea la respuesta con los resultados de outliers."""
        response = f"✅ **Análisis de Outliers Completado**\n\n"
        response += f"📊 **Resumen:**\n"
        response += f"- Año Base: {params['base_year']}\n"
        response += f"- Periodo: {params['start_date']} → {params['end_date']}\n"
        response += f"- Umbral: >{params['threshold']}%\n"
        response += f"- **Medidores encontrados: {len(results)}**\n\n"
        
        if len(results) > 5:
            response += f"📋 **Top 5 Medidores con Mayores Desviaciones:**\n\n"
            display_results = results[:5]
        else:
            response += f"📋 **Medidores Identificados:**\n\n"
            display_results = results
        
        for i, result in enumerate(display_results, 1):
            medidor_info = result['medidor_info']
            response += f"**{i}. {result['device_id']}** - {medidor_info['description']}\n"
            response += f"   🔸 Desviación: **{result['max_deviation']:.1f}%**\n"
            response += f"   🔸 Cliente: {medidor_info['customerid']}\n"
            response += f"   🔸 Fecha análisis: {result['fecha']}\n\n"
        
        if len(results) > 5:
            response += f"... y **{len(results) - 5} medidores** más con desviaciones significativas.\n\n"
        
        response += "💡 **Nota:** Datos disponibles para análisis detallado de curvas de carga."
        
        return response

    def _classify_intent_with_gemini(self, message: str) -> str:
        """Usa Gemini para clasificar la intención del mensaje en categorías específicas."""
        try:
            classification_prompt = f"""
Analiza la siguiente consulta y clasifícala en una de estas categorías:

- "demand_growth": Consultas sobre crecimiento/comparación de demanda entre periodos, como "medidores con mayor crecimiento", "comparación de semanas", "aumento de demanda"
- "outlier": Consultas sobre búsqueda de outliers, desviaciones, anomalías, medidores que exceden umbrales
- "max_power": Consultas sobre máxima potencia, potencia pico, máximo de potencia
- "total_energy": Consultas sobre energía total, consumo total, suma de energía, demanda de energía
- "general": Preguntas generales sobre conceptos eléctricos, eficiencia energética, o cualquier otra cosa

Consulta: "{message}"

Responde SOLO con una de estas palabras: demand_growth, outlier, max_power, total_energy, general
"""
            
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=classification_prompt
            )
            
            intent = response.text.strip().lower()
            print(f"[DEBUG] Gemini clasificó la intención como: {intent}")
            return intent
            
        except Exception as e:
            print(f"[DEBUG] Error clasificando intención con Gemini: {e}")
            return "general"

    def _build_prompt(self, message: str, context: dict = None) -> str:
        base = """Actúa como un ingeniero electricista experto en análisis de demanda y eficiencia energética. Responde de forma clara, técnica y útil.

SERVICIOS DISPONIBLES (con endpoints implementados):
- **Análisis de crecimiento de demanda**: Comparar consumo entre periodos (primera semana vs mes anterior, etc.)
- **Búsqueda de outliers**: Medidores con desviaciones significativas (>X%) respecto a un año base
- **Máxima potencia**: Potencia máxima registrada por un medidor en un periodo específico
- **Energía total**: Consumo total de energía (kWh) de un medidor en un periodo
- **Información de medidores**: Lista de medidores disponibles y sus datos

SERVICIOS NO DISPONIBLES:
- Predicción meteorológica
- Análisis de facturas eléctricas
- Recomendaciones de tecnologías eficientes
- Cálculo de retorno de inversión
- Optimización de consumo específica por equipo

Si la pregunta está fuera del ámbito de los servicios disponibles, responde claramente indicando las limitaciones."""
        
        if context:
            base += "\n\nContexto relevante:\n"
            for k, v in context.items():
                base += f"- {k}: {v}\n"
        base += f"\n\nPregunta del usuario: {message}\n"
        base += "Responde en español. Si la pregunta es sobre conceptos eléctricos, explica de forma sencilla y técnica."
        return base

    def _handle_demand_growth_query(self, message: str) -> str:
        """Procesa consultas sobre crecimiento de demanda usando EnergyService."""
        if not self.energy_service:
            return "Error: No tengo acceso al servicio de análisis energético para buscar datos reales."
        
        try:
            # Extraer parámetros de la consulta
            params = self._extract_demand_growth_params(message)
            
            if not all([params['current_start'], params['current_end'], params['previous_start'], params['previous_end']]):
                return "Error: No pude extraer todos los parámetros necesarios. Por favor, especifica claramente los periodos a comparar (ej: 'primera semana de noviembre vs primera semana de octubre')."
            
            # Informar que se está procesando
            print(f"Procesando consulta de crecimiento de demanda: {params}")
            
            # Ejecutar análisis de crecimiento de demanda
            results = self.energy_service.analyze_demand_growth(
                current_period_start=params['current_start'],
                current_period_end=params['current_end'],
                previous_period_start=params['previous_start'],
                previous_period_end=params['previous_end'],
                min_growth_percentage=params['min_growth']
            )
            
            if not results:
                return f"✅ **Análisis Completado**\n\nNo se encontraron medidores con crecimiento de demanda significativo en la comparación entre:\n- **Periodo actual:** {params['current_start']} a {params['current_end']}\n- **Periodo anterior:** {params['previous_start']} a {params['previous_end']}"
            
            # Formatear respuesta
            return self._format_demand_growth_response(results, params)
            
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return "❌ **Error de Timeout**\n\nLa consulta tardó demasiado tiempo. Intenta reducir el rango de fechas o contacta al administrador."
            elif "database" in error_msg.lower():
                return "❌ **Error de Base de Datos**\n\nNo se pudo conectar a la base de datos. Verifica que el servicio esté funcionando."
            else:
                return f"❌ **Error procesando la consulta:** {error_msg}"

    def _extract_demand_growth_params(self, message: str):
        """Extrae parámetros de consultas de crecimiento de demanda."""
        params = {
            'current_start': None,
            'current_end': None,
            'previous_start': None,
            'previous_end': None,
            'min_growth': 0.0
        }
        
        # Función auxiliar para calcular primera semana del mes
        def get_first_week_of_month(year: int, month: int):
            """Calcula las fechas de la primera semana de un mes (lunes a domingo)."""
            from datetime import datetime, timedelta
            
            # Primer día del mes
            first_day = datetime(year, month, 1)
            
            # Encontrar el lunes de la primera semana
            # Si el primer día no es lunes, retroceder hasta encontrar el lunes
            first_monday = first_day
            while first_monday.weekday() != 0:  # 0 es lunes
                first_monday -= timedelta(days=1)
            
            # El domingo de la primera semana es 6 días después del lunes
            first_sunday = first_monday + timedelta(days=6)
            
            # Si el domingo está en el mes siguiente, ajustar al último día del mes actual
            if first_sunday.month != month:
                # Último día del mes actual
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                first_sunday = last_day
            
            return first_monday.strftime("%Y-%m-%d"), first_sunday.strftime("%Y-%m-%d")
        
        # Función auxiliar para detectar meses por nombre
        def detect_month_by_name(text):
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            text_lower = text.lower()
            for mes_nombre, mes_numero in meses.items():
                if mes_nombre in text_lower:
                    return mes_numero
            return None
        
        # Detectar patrón "primera semana de [mes actual] vs primera semana del mes anterior" - versión más flexible
        growth_patterns = [
            # Patrones que incluyen "mayor crecimiento" y "demanda"
            r'mayor\s+crecimiento.*?demanda.*?primera\s+semana\s+(?:de\s+)?(\w+).*?comparaci[oó]n.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            r'crecimiento.*?demanda.*?primera\s+semana\s+(?:de\s+)?(\w+).*?comparaci[oó]n.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            # Patrones que capturan la estructura con "el la"
            r'(?:el\s+)?la\s+primera\s+semana\s+(?:de\s+)?(\w+).*?comparaci[oó]n.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            # Patrones generales
            r'primera\s+semana\s+(?:de\s+)?(\w+).*?comparaci[oó]n.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:de\s+)?(\w+).*?en\s+comparaci[oó]n.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:de\s+)?(\w+).*?comparada.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:de\s+)?(\w+).*?versus.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:de\s+)?(\w+).*?vs.*?primera\s+semana\s+(?:de\s+)?(?:el\s+)?mes\s+anterior',
            # Patrones más flexibles para variaciones comunes
            r'primera\s+semana\s+(?:del?\s+)?(\w+).*?comparaci[oó]n.*?primera\s+semana\s+(?:del?\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:del?\s+)?(\w+).*?en\s+comparaci[oó]n.*?primera\s+semana\s+(?:del?\s+)?mes\s+anterior',
            r'primera\s+semana\s+(?:del?\s+)?(\w+).*?comparada.*?primera\s+semana\s+(?:del?\s+)?mes\s+anterior'
        ]
        
        for pattern in growth_patterns:
            growth_match = re.search(pattern, message, re.IGNORECASE)
            if growth_match:
                current_month_name = growth_match.group(1).lower()
                print(f"[DEBUG] Patrón detectado: mes actual = '{current_month_name}'")
                
                current_month = detect_month_by_name(current_month_name)
                print(f"[DEBUG] Mes detectado numérico: {current_month}")
                
                if current_month:
                    # Determinar año (asumir año actual)
                    from datetime import datetime
                    current_year = datetime.now().year
                    
                    # Calcular mes anterior
                    if current_month == 1:
                        previous_month = 12
                        previous_year = current_year - 1
                    else:
                        previous_month = current_month - 1
                        previous_year = current_year
                    
                    # Calcular semanas
                    current_start, current_end = get_first_week_of_month(current_year, current_month)
                    previous_start, previous_end = get_first_week_of_month(previous_year, previous_month)
                    
                    params['current_start'] = current_start
                    params['current_end'] = current_end
                    params['previous_start'] = previous_start
                    params['previous_end'] = previous_end
                    params['min_growth'] = 0.0  # Mostrar todos los crecimientos
                    
                    print(f"[DEBUG] Crecimiento detectado: {current_month_name} {current_year} vs mes anterior {previous_year}-{previous_month:02d}")
                    print(f"[DEBUG] Fechas calculadas: actual={current_start} a {current_end}, anterior={previous_start} a {previous_end}")
                    return params
                else:
                    print(f"[DEBUG] No se pudo detectar el mes: '{current_month_name}'")
                break
        
        # Detectar patrón alternativo "primera semana de [mes actual] vs primera semana de [mes anterior]"
        growth_match_alt = re.search(r'primera\s+semana\s+(?:de\s+)?(\w+).*comparaci[oó]n.*primera\s+semana\s+(?:de\s+)?(\w+)', message, re.IGNORECASE)
        if growth_match_alt:
            current_month_name = growth_match_alt.group(1).lower()
            previous_month_name = growth_match_alt.group(2).lower()
            
            current_month = detect_month_by_name(current_month_name)
            previous_month = detect_month_by_name(previous_month_name)
            
            if current_month and previous_month:
                # Determinar año (asumir año actual para ambos)
                from datetime import datetime
                current_year = datetime.now().year
                
                # Si el mes actual es enero y el anterior es diciembre, ajustar años
                if current_month == 1 and previous_month == 12:
                    previous_year = current_year - 1
                else:
                    previous_year = current_year
                
                # Calcular semanas
                current_start, current_end = get_first_week_of_month(current_year, current_month)
                previous_start, previous_end = get_first_week_of_month(previous_year, previous_month)
                
                params['current_start'] = current_start
                params['current_end'] = current_end
                params['previous_start'] = previous_start
                params['previous_end'] = previous_end
                params['min_growth'] = 0.0  # Mostrar todos los crecimientos
                
                print(f"[DEBUG] Crecimiento detectado: {current_month_name} {current_year} vs {previous_month_name} {previous_year}")
                return params
        
        # Buscar años mencionados
        year_match = re.findall(r'\b(20[012]\d)\b', message)
        if year_match:
            # Si hay años, usar lógica similar pero con años específicos
            pass
        
        return params

    def _format_demand_growth_response(self, results, params):
        """Formatea la respuesta con los resultados de crecimiento de demanda."""
        response = f"✅ **Análisis de Crecimiento de Demanda Completado**\n\n"
        response += f"📊 **Comparativa de Periodos:**\n"
        response += f"- **Periodo Actual:** {params['current_start']} → {params['current_end']}\n"
        response += f"- **Periodo Anterior:** {params['previous_start']} → {params['previous_end']}\n"
        response += f"- **Medidores con Crecimiento:** {len(results)}\n\n"
        
        if len(results) > 10:
            response += f"📋 **Top 10 Medidores con Mayor Crecimiento:**\n\n"
            display_results = results[:10]
        else:
            response += f"📋 **Medidores con Crecimiento Identificado:**\n\n"
            display_results = results
        
        for i, result in enumerate(display_results, 1):
            response += f"**{i}. {result['device_id']}** - {result['description']}\n"
            response += f"   📈 **Crecimiento:** +{result['growth_percentage']:.1f}%\n"
            response += f"   🔸 **Energía Actual:** {result['current_period_energy']:,.0f} kWh\n"
            response += f"   🔸 **Energía Anterior:** {result['previous_period_energy']:,.0f} kWh\n"
            response += f"   👤 **Cliente:** {result['customerid']}\n\n"
        
        if len(results) > 10:
            response += f"... y **{len(results) - 10} medidores** más con crecimiento positivo.\n\n"
        
        response += "💡 **Nota:** Este análisis compara el consumo energético total entre periodos equivalentes."
        
        return response
