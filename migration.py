from playhouse.migrate import *

my_db = SqliteDatabase('traders.db')
migrator = SqliteMigrator(my_db)

isClear = IntegerField(default=0)

with my_db.transaction():
    migrate(
        migrator.add_column('Userstatus', 'isClear', isClear),
    )