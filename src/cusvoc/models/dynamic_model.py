from peewee import Model, Database
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class DynamicModel(Model):
    """A base model that dynamically assigns the database."""

    @classmethod
    def set_database(cls, db: Database):
        cls._meta.database = db
    
    @classmethod
    def set_table_name(cls, name: str):
        cls._meta.table_name = name

    @classmethod
    def connect_db(cls, db: Database, table_name: str):  # Ensure cls is the first argument
        cls.set_database(db=db)  # Use cls instead of DynamicModel
        cls.set_table_name(name=table_name)