from peewee import SqliteDatabase
from peewee import CharField, BooleanField, IntegerField, FloatField

from playhouse.migrate import SqliteMigrator, migrate

DB_PATH = '../data/vocabulary.db'


my_db = SqliteDatabase(DB_PATH)
migratory = SqliteMigrator(database=my_db)

was_practiced_field = BooleanField(null=True, default=False)

if __name__ == "__main__":
    
    migrate(
        migratory.add_column(table='lexical_entries', column_name='was_practiced', field=was_practiced_field)
    )

