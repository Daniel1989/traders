import datetime

from playhouse.migrate import *
from dotenv import load_dotenv
import os

from models import DailyAccount

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
database = MySQLDatabase('futures', user=db_user, password=db_password,
                         host=db_host, port=3306)
migrator = MySQLMigrator(database)


def formatted_datetime_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


symbol = CharField(null=True)
exchange = CharField(null=True)
create_time = DateTimeField(default=formatted_datetime_now)

with database.transaction():
    migrate(
        # migrator.add_column('daily_trade', 'symbol', symbol),
        migrator.add_column('records', 'create_time', create_time),
        # migrator.add_index('daily_trade', ['create_time', 'code_no', 'date'], True)

    )

    # Migrate data from old_field to new_field
    # DailyAccount.update(value=DailyAccount.value.cast(FloatField())).execute()

    # Drop old_field
    # migrate(
    #     migrator.drop_column('daily_account', 'value2')
    # )
