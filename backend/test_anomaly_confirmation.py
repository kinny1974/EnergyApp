"""
Test para validar el flujo de confirmación en búsqueda de anomalías
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat_service import ChatService
from app.services.energy_service import EnergyService
from app.data.repositories import EnergyRepository
from app.data.database import SessionLocal

def print_separator(title=""):
    print("\n" + "=" * 74)
    print("=" * 6 + " " * 60 + title)
    print("=" * 74)

def print_result(result):
    """Imprime el resultado de forma estructurada."""
    print(f"✅ Tipo: {result.get('type', 'N/A')}")
    if result.get('parameters'):
        print(f"📊 Parámetros: {result['parameters']}")
    print(f"\n💬 Respuesta:\n{result.get('response', result.get('message', 'N/A'))}")

def main():
    print("\n🚀 Test de confirmación para búsqueda de anomalías")
    
    # Inicializar servicios
    db = SessionLocal()
    repo = EnergyRepository(db)
    energy_service = EnergyService(repo)
    chat_service = ChatService(energy_service)
    
    print_separator()
    print(f"📊 Medidores activos en el sistema: {repo.count_active_medidores()}")
    print_separator()
    
    # Test 1: Primera solicitud (sin confirmación)
    print_separator()
    print("📝 Test 1: Solicitud inicial de anomalías (debería pedir confirmación)")
    print_separator()
    
    query1 = "Medidores con anomalías en julio 2024"
    result1 = chat_service.ask_gemini(query1)
    print_result(result1)
    
    # Verificar que pide confirmación
    if result1.get('type') == 'confirmation_required':
        print("\n✅ CORRECTO: El sistema pidió confirmación antes de procesar")
        print(f"⏱️  Tiempo estimado: {result1['parameters']['estimated_minutes']:.1f} minutos")
        print(f"📊 Total medidores: {result1['parameters']['total_medidores']}")
        print(f"📅 Días a analizar: {result1['parameters']['days']}")
        print(f"📆 Año base: {result1['parameters']['base_year']}")
        
        # Test 2: Respuesta de confirmación
        print_separator()
        print("📝 Test 2: Usuario confirma la operación")
        print_separator()
        
        query2 = "Sí, confirmar"
        result2 = chat_service.ask_gemini(query2)
        
        # Verificar que ahora está procesando
        if result2.get('type') == 'anomalies' or result2.get('type') == 'error':
            print("✅ CORRECTO: El sistema procesó la confirmación")
            print_result(result2)
        else:
            print(f"❌ ERROR: Tipo de respuesta inesperado: {result2.get('type')}")
            print_result(result2)
    else:
        print("\n❌ ERROR: El sistema NO pidió confirmación")
        print(f"Tipo recibido: {result1.get('type')}")
    
    print_separator()
    print("✅ Test completado")
    print_separator()
    
    db.close()

if __name__ == "__main__":
    main()
