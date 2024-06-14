from playhouse.migrate import *

my_db = SqliteDatabase('traders.db')
migrator = SqliteMigrator(my_db)

close_date = CharField(null=True, default=None)
open_date = CharField()

with my_db.transaction():
    migrate(
        migrator.add_column('Userstatus', 'close_date', close_date),
        migrator.add_column('Userstatus', 'open_date', open_date),
    )