from sqlmodel import Session, select
from app.database import engine
from app.models import Goods, GoodsPriceInSecond
import sqlalchemy as sa
from sqlalchemy import text

def add_title_column():
    """Add title column to goods table while preserving existing data"""
    try:
        # Create a new connection
        with engine.connect() as conn:
            # Check if title column exists
            inspector = sa.inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('goods')]
            
            if 'title' not in columns:
                print("Adding 'title' column to goods table...")
                # Add the new column
                conn.execute(text("ALTER TABLE goods ADD COLUMN title VARCHAR(255)"))
                conn.commit()
                print("Successfully added 'title' column")
            else:
                print("Title column already exists")
            
            return "Migration completed successfully"
            
    except Exception as e:
        return f"Migration failed: {str(e)}"

def main():
    print("Starting migration...")
    result = add_title_column()
    print(result)

if __name__ == "__main__":
    main() 