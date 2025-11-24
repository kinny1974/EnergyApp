#!/usr/bin/env python3

"""
Script para probar múltiples escenarios del chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

def test_scenario(db, chat_service, message, expected_type=None):
    """
    Prueba un escenario específico del chatbot
    """
    print(f"\n📝 Consulta: {message}")
    print("=" * 80)
    
    try:
        result = chat_service.ask_gemini(message)
        
        print(f"✅ Tipo de respuesta: {result.get('type', 'N/A')}")
        print(f"📊 Parámetros: {result.get('parameters', 'N/A')}")
        print(f"💬 Respuesta:\n{result.get('response', 'N/A')}")
        
        if expected_type and result.get('type') == expected_type:
            print(f"✅ TEST PASSED: Tipo esperado '{expected_type}' coincide")
        elif expected_type:
            print(f"❌ TEST FAILED: Se esperaba '{expected_type}' pero se obtuvo '{result.get('type')}'")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Iniciando pruebas de múltiples escenarios del chatbot")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        repo = EnergyRepository(db)
        energy_service = EnergyService(repo)
        chat_service = ChatService(energy_service)
        
        # ESCENARIO 1: Consulta de mes completo (agosto 2024)
        test_scenario(
            db, chat_service,
            "¿Cuánta energía consumió el medidor 36075003 en agosto 2024?",
            expected_type="total_energy"
        )
        
        # ESCENARIO 2: Consulta de otro mes (julio 2024)
        test_scenario(
            db, chat_service,
            "Energía del medidor 36075003 en julio de 2024",
            expected_type="total_energy"
        )
        
        # ESCENARIO 3: Consulta con formato diferente
        test_scenario(
            db, chat_service,
            "Consumo de 36075003 en septiembre 2024",
            expected_type="total_energy"
        )
        
        # ESCENARIO 4: Consulta sin información completa
        test_scenario(
            db, chat_service,
            "¿Cuánta energía consumió en agosto 2024?",
            expected_type="clarification_needed"
        )
        
        # ESCENARIO 5: Consulta de potencia máxima
        test_scenario(
            db, chat_service,
            "¿Cuál fue la potencia máxima del medidor 36075003 en agosto 2024?",
            expected_type="max_power"
        )
        
        # ESCENARIO 6: Consulta general
        test_scenario(
            db, chat_service,
            "¿Qué puedes hacer?",
            expected_type="general"
        )
        
        # ESCENARIO 7: Comparación de curvas de carga
        test_scenario(
            db, chat_service,
            "Compara la curva de carga del día 20 de octubre de 2025, con la curva de carga promedio para el año 2024, del medidor 36075003",
            expected_type="load_curve_comparison"
        )
        
        print("\n" + "=" * 80)
        print("✅ Pruebas completadas")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
