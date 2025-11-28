"""
Script de prueba para detección de anomalías en medidores
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.data.database import get_db
from app.data.repositories import EnergyRepository
from app.services.energy_service import EnergyService
from app.services.chat_service import ChatService

def main():
    print("🚀 Prueba de detección de anomalías")
    print("=" * 80)
    
    # Inicializar servicios
    db = next(get_db())
    repo = EnergyRepository(db)
    energy_service = EnergyService(repo)
    chat_service = ChatService(energy_service)
    
    # Consultas de prueba
    test_queries = [
        "Medidores con anomalías en julio 2024",
        "¿Qué medidores tuvieron anomalías en agosto 2024 comparado con 2023?",
        "Busca medidores con desviaciones en octubre 2024",
    ]
    
    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"📝 Consulta: {query}")
        print("=" * 80)
        
        result = chat_service.ask_gemini(query)
        
        print(f"✅ Tipo: {result['type']}")
        if result.get('parameters'):
            print(f"📊 Parámetros: {result['parameters']}")
        print(f"\n💬 Respuesta:\n{result['response']}")
        
        # Si hay datos de anomalías, mostrar resumen
        if result.get('anomalies_data'):
            anomalies = result['anomalies_data']
            print(f"\n📈 Total de anomalías encontradas: {len(anomalies)}")
            if len(anomalies) > 0:
                print(f"   Primera anomalía: Medidor {anomalies[0]['device_id']} - "
                      f"Desviación: {anomalies[0]['max_deviation']:.2f}%")
    
    print("\n" + "=" * 80)
    print("✅ Pruebas completadas")
    print("=" * 80)

if __name__ == "__main__":
    main()
