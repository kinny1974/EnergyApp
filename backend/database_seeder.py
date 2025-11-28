#!/usr/bin/env python3
"""
Database Seeder for Energy App
Handles initial data population for m_lecturas 2024-2025 data
"""

import os
import sys
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.database import SessionLocal, engine
from app.data.models import Departamento, Municipio, Localidad, Medidor, MLectura
from app.data.repositories import EnergyRepository

def create_sample_departments(db: Session):
    """Create sample departments"""
    print("🏢 Creating sample departments...")
    
    departments = [
        {"id_dep": "05", "departamento": "Antioquia"},
        {"id_dep": "11", "departamento": "Bogotá D.C."},
        {"id_dep": "76", "departamento": "Valle del Cauca"},
        {"id_dep": "08", "departamento": "Atlántico"},
    ]
    
    for dept_data in departments:
        dept = Departamento(**dept_data)
        db.merge(dept)
    
    db.commit()
    print(f"✅ Created {len(departments)} departments")

def create_sample_municipalities(db: Session):
    """Create sample municipalities"""
    print("🏘️ Creating sample municipalities...")
    
    municipalities = [
        # Antioquia
        {"id_mun": "05001", "id_dep": "05", "municipio": "Medellín"},
        {"id_mun": "05266", "id_dep": "05", "municipio": "Envigado"},
        {"id_mun": "05360", "id_dep": "05", "municipio": "Itagüí"},
        
        # Bogotá
        {"id_mun": "11001", "id_dep": "11", "municipio": "Bogotá"},
        
        # Valle del Cauca
        {"id_mun": "76001", "id_dep": "76", "municipio": "Cali"},
        {"id_mun": "76520", "id_dep": "76", "municipio": "Palmira"},
        
        # Atlántico
        {"id_mun": "08001", "id_dep": "08", "municipio": "Barranquilla"},
    ]
    
    for mun_data in municipalities:
        mun = Municipio(**mun_data)
        db.merge(mun)
    
    db.commit()
    print(f"✅ Created {len(municipalities)} municipalities")

def create_sample_localities(db: Session):
    """Create sample localities"""
    print("🏠 Creating sample localities...")
    
    localities = [
        # Medellín localities
        {"id_loc": "050010001", "id_mun": "05001", "localidad": "El Poblado", "clas_politica": "UR", "latitud": 6.2086, "longitud": -75.5678},
        {"id_loc": "050010002", "id_mun": "05001", "localidad": "Laureles", "clas_politica": "UR", "latitud": 6.2500, "longitud": -75.5833},
        {"id_loc": "050010003", "id_mun": "05001", "localidad": "Centro", "clas_politica": "UR", "latitud": 6.2442, "longitud": -75.5736},
        
        # Bogotá localities
        {"id_loc": "110010001", "id_mun": "11001", "localidad": "Chapinero", "clas_politica": "UR", "latitud": 4.6483, "longitud": -74.0619},
        {"id_loc": "110010002", "id_mun": "11001", "localidad": "Usaquén", "clas_politica": "UR", "latitud": 4.6936, "longitud": -74.0333},
        
        # Cali localities
        {"id_loc": "760010001", "id_mun": "76001", "localidad": "San Fernando", "clas_politica": "UR", "latitud": 3.4516, "longitud": -76.5319},
    ]
    
    for loc_data in localities:
        loc = Localidad(**loc_data)
        db.merge(loc)
    
    db.commit()
    print(f"✅ Created {len(localities)} localities")

def create_sample_medidores(db: Session):
    """Create sample medidores"""
    print("📊 Creating sample medidores...")
    
    medidores = [
        {"id_loc": "050010001", "deviceid": "MED001", "devicetype": "Smart Meter", "description": "Medidor Comercial El Poblado", "connectiontype": "GPRS", "customerid": "CUST001", "usergroup": "01", "ipaddress": "192.168.1.101", "port": 502, "activado": datetime(2023, 1, 1), "ke": 1.0},
        {"id_loc": "050010002", "deviceid": "MED002", "devicetype": "Smart Meter", "description": "Medidor Residencial Laureles", "connectiontype": "GPRS", "customerid": "CUST002", "usergroup": "02", "ipaddress": "192.168.1.102", "port": 502, "activado": datetime(2023, 1, 1), "ke": 1.0},
        {"id_loc": "110010001", "deviceid": "MED003", "devicetype": "Smart Meter", "description": "Medidor Comercial Chapinero", "connectiontype": "GPRS", "customerid": "CUST003", "usergroup": "01", "ipaddress": "192.168.1.103", "port": 502, "activado": datetime(2023, 1, 1), "ke": 1.0},
        {"id_loc": "760010001", "deviceid": "MED004", "devicetype": "Smart Meter", "description": "Medidor Industrial San Fernando", "connectiontype": "GPRS", "customerid": "CUST004", "usergroup": "03", "ipaddress": "192.168.1.104", "port": 502, "activado": datetime(2023, 1, 1), "ke": 1.0}
    ]
    
    for med_data in medidores:
        med = Medidor(**med_data)
        db.merge(med)
    
    db.commit()
    print(f"✅ Created {len(medidores)} medidores")

def generate_sample_readings_2024_2025(db: Session):
    """Generate sample m_lecturas data for 2024-2025"""
    print("📈 Generating sample m_lecturas for 2024-2025...")
    
    device_ids = ["MED001", "MED002", "MED003", "MED004"]
    repository = EnergyRepository(db)
    
    total_readings = 0
    
    # Generate data for 2024 and 2025
    for year in [2024, 2025]:
        print(f"  📅 Generating data for {year}...")
        
        # Start from January 1st of the year
        current_date = datetime(year, 1, 1, 0, 0, 0)
        end_date = datetime(year, 12, 31, 23, 45, 0)  # Until Dec 31st
        
        # Generate readings every 15 minutes for each device
        while current_date <= end_date:
            for device_id in device_ids:
                # Generate realistic kWh values based on device type and time of day
                base_kwh = 0.5  # Base consumption
                
                # Time of day variations
                hour = current_date.hour
                if 6 <= hour < 9:  # Morning peak
                    base_kwh += random.uniform(0.8, 1.5)
                elif 18 <= hour < 22:  # Evening peak
                    base_kwh += random.uniform(1.0, 2.0)
                else:  # Off-peak
                    base_kwh += random.uniform(0.1, 0.5)
                
                # Device-specific variations
                if device_id == "MED001":  # Commercial
                    base_kwh *= 2.0
                elif device_id == "MED004":  # Industrial
                    base_kwh *= 3.0
                
                # Weekend variations
                if current_date.weekday() >= 5:  # Weekend
                    base_kwh *= 0.7  # Lower consumption on weekends
                
                # Add some random noise
                kwhd = round(base_kwh + random.uniform(-0.1, 0.1), 3)
                kvarhd = round(kwhd * 0.1 + random.uniform(-0.05, 0.05), 3)  # Reactive power
                
                # Create reading
                reading = MLectura(
                    fecha=current_date,
                    deviceid=device_id,
                    kwhd=kwhd,
                    kvarhd=kvarhd
                )
                
                db.merge(reading)
                total_readings += 1
            
            # Commit every 1000 readings to avoid memory issues
            if total_readings % 1000 == 0:
                db.commit()
                print(f"    ✅ Committed {total_readings} readings so far...")
            
            # Move to next 15-minute interval
            current_date += timedelta(minutes=15)
    
    # Final commit
    db.commit()
    print(f"✅ Generated {total_readings} sample readings for 2024-2025")

def seed_database():
    """Main database seeding function"""
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_medidores = db.query(Medidor).count()
        existing_readings = db.query(MLectura).count()
        
        if existing_medidores > 0:
            print(f"⚠️ Database already has {existing_medidores} medidores, skipping seeding")
            if existing_readings == 0:
                print("📊 No readings found, generating sample readings...")
                generate_sample_readings_2024_2025(db)
            return
        
        # Create sample data
        create_sample_departments(db)
        create_sample_municipalities(db)
        create_sample_localities(db)
        create_sample_medidores(db)
        generate_sample_readings_2024_2025(db)
        
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()