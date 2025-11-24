#!/usr/bin/env python3

"""
Script para probar directamente el chatbot y diagnosticar el problema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

def test_chatbot_august_2024():
    """
    Prueba el chatbot con la consulta que no está funcionando
    """
    print("🔍 Iniciando prueba del chatbot...")
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Crear instancias de servicios
        repo = EnergyRepository(db)
        energy_service = EnergyService(repo)
        chat_service = ChatService(energy_service)
        
        # Mensaje de prueba
        test_message = "¿Cuánta energía consumió el medidor 36075003 en agosto 2024?"
        
        print(f"📝 Mensaje de prueba: {test_message}")
        print("=" * 60)
        
        # Llamar al chatbot
        result = chat_service.ask_gemini(test_message)
        
        print("📊 Resultado del chatbot:")
        print(f"Tipo: {result.get('type', 'N/A')}")
        print(f"Parámetros: {result.get('parameters', 'N/A')}")
        print(f"Respuesta: {result.get('response', 'N/A')}")
        
        print("=" * 60)
        
        # Ahora probemos directamente el repositorio
        print("🔧 Probando directamente el repositorio...")
        direct_result = repo.get_total_energy_in_period(
            device_id='36075003',
            start_date='2024-08-01',
            end_date='2024-08-31'
        )
        
        print(f"📈 Resultado directo del repositorio: {direct_result}")
        
        return result, direct_result
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    finally:
        db.close()

def test_message_analysis():
    """
    Prueba específica del análisis del mensaje
    """
    print("\n🧪 Análisis específico del mensaje...")
    
    test_message = "¿Cuánta energía consumió el medidor 36075003 en agosto 2024?"
    message_lower = test_message.lower()
    
    print(f"Mensaje original: {test_message}")
    print(f"Mensaje en minúsculas: {message_lower}")
    
    # Verificar condiciones que debería cumplir
    energy_words = ['energía', 'consumo', 'kwh']
    has_energy_words = any(word in message_lower for word in energy_words)
    has_device = '36075003' in test_message
    has_august_2024 = 'agosto 2024' in message_lower
    
    print(f"¿Tiene palabras de energía? {has_energy_words}")
    print(f"¿Tiene deviceid 36075003? {has_device}")
    print(f"¿Tiene 'agosto 2024'? {has_august_2024}")
    
    # Buscar patrones específicos que el chatbot busca
    specific_patterns = [
        '1 de noviembre de 2025',
        'mes de noviembre de 2025',
        'noviembre de 2025',
        'último lunes',
        'primer lunes',
        'último martes',
        'primer martes'
    ]
    
    found_patterns = [pattern for pattern in specific_patterns if pattern in message_lower]
    print(f"Patrones específicos encontrados: {found_patterns}")
    
    return {
        'has_energy_words': has_energy_words,
        'has_device': has_device,
        'has_august_2024': has_august_2024,
        'found_patterns': found_patterns
    }

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico del chatbot EnergyApp")
    print("=" * 60)
    
    # Primero hacer el análisis del mensaje
    analysis = test_message_analysis()
    
    # Luego probar el chatbot
    chat_result, repo_result = test_chatbot_august_2024()
    
    print("\n📋 RESUMEN DEL DIAGNÓSTICO:")
    print("=" * 60)
    
    if analysis['has_energy_words'] and analysis['has_device']:
        print("✅ El mensaje contiene palabras de energía y el device_id")
    else:
        print("❌ El mensaje NO contiene las palabras necesarias")
    
    if not analysis['has_august_2024']:
        print("⚠️  PROBLEMA ENCONTRADO: El chatbot no reconoce 'agosto 2024'")
        print("   El chatbot solo reconoce patrones específicos como 'noviembre de 2025'")
        print("   pero no tiene lógica para otros meses/años.")
    
    if repo_result:
        print(f"✅ Los datos SÍ existen en la base de datos: {repo_result['total_energy_kwh']} kWh")
    else:
        print("❌ No hay datos en la base de datos")
    
    print("\n🔧 CAUSA RAÍZ IDENTIFICADA:")
    print("   El chatbot tiene lógica hardcodeada solo para fechas específicas")
    print("   (noviembre 2025, último lunes de mayo, etc.) pero no tiene")
    print("   lógica general para interpretar fechas como 'agosto 2024'.")