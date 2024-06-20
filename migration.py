from playhouse.migrate import *

my_db = SqliteDatabase('traders.db')
migrator = SqliteMigrator(my_db)

type = CharField(default="5MIN")

with my_db.transaction():
    migrate(
        migrator.add_column('PriceRecord', 'type', type),
    )