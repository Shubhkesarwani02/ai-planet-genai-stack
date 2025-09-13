#!/usr/bin/env python3
"""
Initialize database with proper schema
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    """Initialize database with the correct schema"""
    try:
        print("Initializing database...")
        from app.db.database import engine, init_db
        from app.db.models import Base
        from sqlalchemy import text
        
        # Connect to database
        with engine.connect() as connection:
            # Drop existing app tables if they exist
            print("Dropping existing app tables if they exist...")
            connection.execute(text("DROP TABLE IF EXISTS chat_logs CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS workspaces CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS app_users CASCADE"))
            connection.commit()
        
        # Create all tables
        print("Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✓ Database initialized successfully!")
        
        # Verify the schema
        with engine.connect() as connection:
            result = connection.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'app_users'"))
            columns = result.fetchall()
            
            print("\nNew 'app_users' table schema:")
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")
        
        return True
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    initialize_database()