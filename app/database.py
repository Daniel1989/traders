from sqlmodel import create_engine, Session, SQLModel
from os import environ
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.exc import OperationalError
from typing import Optional

load_dotenv()

DATABASE_URL = environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def init_db(drop_tables: bool = False) -> Optional[str]:
    print(f"Initializing database with URL: {DATABASE_URL}")
    """
    Initialize database tables
    Args:
        drop_tables: If True, drop existing tables before creating new ones
    Returns:
        Optional error message if something goes wrong
    """
    try:
        if drop_tables:
            SQLModel.metadata.drop_all(engine)
            print("Dropped all existing tables")
        
        # Get list of existing tables
        inspector = sqlalchemy.inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Check which tables need to be created
        tables_to_create = []
        for table in SQLModel.metadata.tables.values():
            if table.name not in existing_tables:
                tables_to_create.append(table.name)
        
        if not tables_to_create:
            return "All tables already exist, no action needed"
        
        # Create only new tables
        SQLModel.metadata.create_all(engine)
        return f"Created new tables: {', '.join(tables_to_create)}"
        
    except OperationalError as e:
        return f"Database connection error: {str(e)}"
    except Exception as e:
        return f"Error initializing database: {str(e)}"

def get_session():
    with Session(engine) as session:
        yield session 