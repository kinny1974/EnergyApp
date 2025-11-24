#!/usr/bin/env python3

"""
Script para probar el endpoint REST del chatbot
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_endpoint(message):
    """
    Prueba el endpoint /chat con un mensaje
    """
    print(f"\n📝 Consulta: {message}")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Tipo: {result.get('type', 'N/A')}")
            print(f"💬 Respuesta:\n{result.get('response', 'N/A')}")
            return result
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor.")
        print("   Asegúrate de que el backend esté corriendo: uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 Prueba del endpoint REST del chatbot")
    print("=" * 80)
    
    # Probar si el servidor está corriendo
    print("\n🔍 Verificando conexión al servidor...")
    try:
        response = requests.get(f"{BASE_URL}/devices", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor corriendo correctamente")
        else:
            print(f"⚠️  Servidor respondió con código {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor en http://localhost:8000")
        print("   Inicia el servidor con: uvicorn app.main:app --reload")
        return
    
    # Pruebas del chatbot
    test_chat_endpoint("¿Cuánta energía consumió el medidor 36075003 en agosto 2024?")
    test_chat_endpoint("Consumo del medidor 36075003 en julio 2024")
    test_chat_endpoint("¿Cuál fue la potencia máxima del medidor 36075003 en agosto 2024?")
    test_chat_endpoint("¿Qué puedes hacer?")
    
    print("\n" + "=" * 80)
    print("✅ Pruebas del endpoint completadas")

if __name__ == "__main__":
    main()
