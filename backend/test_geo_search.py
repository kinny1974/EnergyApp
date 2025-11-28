#!/usr/bin/env python3

"""
Script para probar las nuevas funcionalidades de búsqueda geográfica
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal
from app.data.repositories import EnergyRepository

def test_localidades(repo):
    print("\n" + "="*80)
    print("🏘️  PRUEBA: Búsqueda de Localidades")
    print("="*80)
    
    # Listar todas las localidades
    localidades = repo.get_all_localidades()
    print(f"\n📊 Total de localidades: {len(localidades)}")
    
    if localidades:
        print("\n📋 Primeras 5 localidades:")
        for loc in localidades[:5]:
            municipio = loc.municipio.municipio if loc.municipio else "N/A"
            print(f"   • {loc.localidad} (ID: {loc.id_loc}) - Municipio: {municipio}")
    
    # Buscar localidad por nombre
    search_term = "Inírida"
    print(f"\n🔍 Buscando localidades con término: '{search_term}'")
    results = repo.search_localidades_by_name(search_term)
    print(f"   Resultados encontrados: {len(results)}")
    for loc in results:
        print(f"   • {loc.localidad} (ID: {loc.id_loc})")

def test_medidores_por_localidad(repo):
    print("\n" + "="*80)
    print("⚡ PRUEBA: Medidores por Localidad")
    print("="*80)
    
    localidad_name = "Inírida"
    print(f"\n🔍 Buscando medidores en localidad: '{localidad_name}'")
    medidores = repo.get_medidores_by_localidad(localidad_name)
    print(f"   Medidores encontrados: {len(medidores)}")
    
    if medidores:
        print("\n📋 Lista de medidores:")
        for m in medidores:
            localidad = m.localidad.localidad if m.localidad else "N/A"
            print(f"   • {m.deviceid} - {m.description} (Localidad: {localidad})")

def test_municipios(repo):
    print("\n" + "="*80)
    print("🏙️  PRUEBA: Búsqueda de Municipios")
    print("="*80)
    
    municipios = repo.get_all_municipios()
    print(f"\n📊 Total de municipios: {len(municipios)}")
    
    if municipios:
        print("\n📋 Primeros 5 municipios:")
        for mun in municipios[:5]:
            dep = mun.departamento.departamento if mun.departamento else "N/A"
            print(f"   • {mun.municipio} (ID: {mun.id_mun}) - Departamento: {dep}")

def test_departamentos(repo):
    print("\n" + "="*80)
    print("🗺️  PRUEBA: Búsqueda de Departamentos")
    print("="*80)
    
    departamentos = repo.get_all_departamentos()
    print(f"\n📊 Total de departamentos: {len(departamentos)}")
    
    if departamentos:
        print("\n📋 Lista de departamentos:")
        for dep in departamentos:
            print(f"   • {dep.departamento} (ID: {dep.id_dep})")

def test_search_general(repo):
    print("\n" + "="*80)
    print("🔎 PRUEBA: Búsqueda General de Medidores")
    print("="*80)
    
    search_terms = ["Inírida", "36075003", "Circuito"]
    
    for term in search_terms:
        print(f"\n🔍 Buscando: '{term}'")
        medidores = repo.search_medidores(term)
        print(f"   Resultados encontrados: {len(medidores)}")
        
        if medidores:
            for m in medidores[:3]:  # Mostrar máximo 3
                localidad = m.localidad.localidad if m.localidad else "N/A"
                municipio = m.localidad.municipio.municipio if m.localidad and m.localidad.municipio else "N/A"
                print(f"   • {m.deviceid} - {m.description}")
                print(f"     Localidad: {localidad}, Municipio: {municipio}")

def main():
    print("🚀 Iniciando pruebas de búsqueda geográfica")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        repo = EnergyRepository(db)
        
        test_localidades(repo)
        test_medidores_por_localidad(repo)
        test_municipios(repo)
        test_departamentos(repo)
        test_search_general(repo)
        
        print("\n" + "="*80)
        print("✅ Todas las pruebas completadas exitosamente")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
