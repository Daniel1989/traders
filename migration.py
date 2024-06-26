from playhouse.migrate import *

my_db = SqliteDatabase('traders.db')
migrator = SqliteMigrator(my_db)

cost_time = IntegerField(null=True)

with my_db.transaction():
    migrate(
        migrator.add_column('Ip', 'cost_time', cost_time),
    )