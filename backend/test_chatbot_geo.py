#!/usr/bin/env python3

"""
Script para probar búsquedas geográficas en el chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

def test_query(chat_service, query):
    """Prueba una consulta del chatbot"""
    print(f"\n{'='*80}")
    print(f"📝 Consulta: {query}")
    print('='*80)
    
    try:
        result = chat_service.ask_gemini(query)
        
        print(f"✅ Tipo: {result.get('type', 'N/A')}")
        print(f"📊 Parámetros: {result.get('parameters', 'N/A')}")
        print(f"\n💬 Respuesta:\n{result.get('response', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Pruebas de búsqueda geográfica en el chatbot")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        repo = EnergyRepository(db)
        energy_service = EnergyService(repo)
        chat_service = ChatService(energy_service)
        
        # Test 1: Búsqueda por localidad conocida con único medidor
        test_query(chat_service, "¿Cuál fue el consumo de Isla Múcura en abril de 2024?")
        
        # Test 2: Búsqueda por localidad con múltiples medidores
        test_query(chat_service, "Consumo de Inírida en agosto 2024")
        
        # Test 3: Búsqueda por device_id (debe seguir funcionando)
        test_query(chat_service, "Energía del medidor 36075003 en julio 2024")
        
        # Test 4: Comparación de curva de carga con localidad
        test_query(chat_service, "Compara la curva de carga del día 20 de octubre de 2025 con el promedio de 2024 del medidor 36075003")
        
        print("\n" + "="*80)
        print("✅ Pruebas completadas")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
