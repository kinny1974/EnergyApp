#!/usr/bin/env python3

"""
Script para probar la funcionalidad de comparación de curvas de carga
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

def main():
    print("🚀 Prueba de comparación de curvas de carga")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        repo = EnergyRepository(db)
        energy_service = EnergyService(repo)
        chat_service = ChatService(energy_service)
        
        # Prueba con el prompt del usuario
        message = "compara la curva de carga del día 20 de octubre de 2025, con la curva de carga promedio para el año 2024, del medidor 36075003"
        
        print(f"📝 Consulta: {message}")
        print("=" * 80)
        
        result = chat_service.ask_gemini(message)
        
        print(f"\n✅ Tipo de respuesta: {result.get('type', 'N/A')}")
        print(f"📊 Parámetros: {result.get('parameters', 'N/A')}")
        print(f"\n💬 Respuesta:\n{result.get('response', 'N/A')}")
        
        if result.get('type') == 'load_curve_comparison':
            print("\n✅ TEST PASSED: Comparación de curva de carga ejecutada exitosamente")
        else:
            print(f"\n❌ TEST FAILED: Se esperaba 'load_curve_comparison' pero se obtuvo '{result.get('type')}'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
