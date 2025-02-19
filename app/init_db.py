from app.database import init_db
from app.models import Goods, GoodsPriceInSecond  # Import models to register them
import argparse

def main():
    parser = argparse.ArgumentParser(description='Initialize database tables')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables before creating new ones')
    args = parser.parse_args()

    print("Initializing database...")
    result = init_db(drop_tables=args.drop)
    print(result)

if __name__ == "__main__":
    main() 