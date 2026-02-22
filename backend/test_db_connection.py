def test_connection():
    try:
        from sqlalchemy import create_engine, text
        from app.config import settings
    except ImportError:
        print("\nERROR: Missing backend dependencies (sqlalchemy/pydantic-settings/etc.)")
        print("Install dependencies first:")
        print("  python -m pip install -r requirements.txt\n")
        return False

    print("Testing PostgreSQL connection...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("\n✅ Connection successful!")
            print(f"PostgreSQL version: {version}\n")
            
            # Test database exists
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}\n")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {str(e)}\n")
        print("Common issues:")
        print("1. PostgreSQL service not running")
        print("2. Incorrect password in .env file")
        print("3. Database 'smart_campus' doesn't exist")
        print("4. Firewall blocking port 5432")
        return False

if __name__ == "__main__":
    test_connection()
