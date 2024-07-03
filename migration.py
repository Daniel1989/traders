from playhouse.migrate import *
from dotenv import load_dotenv
import os

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
database = MySQLDatabase('futures', user=db_user, password=db_password,
                                  host=db_host, port=3306)
migrator = MySQLMigrator(database)

model_name = CharField(null=True)

with database.transaction():
    migrate(
        migrator.add_column('startup', 'model_name', model_name),
    )