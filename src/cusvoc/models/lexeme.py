from peewee import CharField

from models.dynamic_model import DynamicModel

class Lexeme(DynamicModel):
    # owner = ForeignKeyField('Person', backref='lexemes')
    string = CharField(unique=True)
    example_sentence = CharField(null=True)
    PAC_file_path = CharField(null=True)