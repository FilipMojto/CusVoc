from peewee import Model

class DynamicModel(Model):
    """A base model that dynamically assigns the database."""

    @classmethod
    def set_database(cls, db):
        cls._meta.database = db
    
    @classmethod
    def set_table_name(cls, name: str):
        cls._meta.table_name = name