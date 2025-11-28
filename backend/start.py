#!/usr/bin/env python3
"""
Startup script for Energy App Backend on Railway
Handles database initialization and server startup
"""

import os
import time
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database_connection():
    """Check if database is available and responsive"""
    print("🔍 Checking database connection...")
    
    # Import database components
    from app.data.database import engine
    from app.data.models import Base
    
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Try to connect to database
            with engine.connect() as conn:
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("💥 Failed to connect to database after multiple attempts")
    return False

def initialize_database():
    """Initialize database tables"""
    print("🗄️ Initializing database tables...")
    
    from app.data.database import engine, Base
    from app.data.models import Departamento, Municipio, Localidad, Medidor, MLectura
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False

def run_migrations():
    """Run any pending database migrations"""
    print("🔄 Checking for database migrations...")
    # Placeholder for future migration system (Alembic)
    # For now, we rely on SQLAlchemy's create_all
    print("✅ No migrations system configured (using SQLAlchemy create_all)")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    
    # Use uvicorn to start the server
    cmd = [
        "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--workers", "1"  # Single worker for Railway
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

def main():
    """Main startup procedure"""
    print("=" * 50)
    print("🔋 Energy App Backend Startup")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"📊 Database URL: {database_url[:20]}..." if database_url else "❌ DATABASE_URL not set")
    print(f"🤖 Gemini API Key: {'✅ Set' if gemini_key else '❌ Not set'}")
    
    # Database initialization sequence
    if not check_database_connection():
        sys.exit(1)
    
    if not initialize_database():
        sys.exit(1)
    
    run_migrations()
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()