"""
Test script para validar búsqueda de anomalías en el chatbot
"""
import sys
import os

# Añadir el directorio raíz al path
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
    print("\n🚀 Pruebas de búsqueda de anomalías en el chatbot")
    
    # Inicializar servicios
    db = SessionLocal()
    repo = EnergyRepository(db)
    energy_service = EnergyService(repo)
    chat_service = ChatService(energy_service)
    
    # Pruebas
    queries = [
        "Medidores con anomalías en julio 2024",
        "¿Qué medidores tuvieron anomalías en agosto de 2024 comparado con 2023?",
        "Buscar anomalías en septiembre 2024",
        "Medidores anormales en octubre 2024",
    ]
    
    for query in queries:
        print_separator()
        print(f"📝 Consulta: {query}")
        print_separator()
        
        result = chat_service.ask_gemini(query)
        print_result(result)
    
    print_separator()
    print("✅ Pruebas completadas")
    print_separator()
    
    db.close()

if __name__ == "__main__":
    main()
