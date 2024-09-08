from peewee import CharField

from models.dynamic_model import DynamicModel



class Collocate(DynamicModel):

    collocate = CharField(unique=True)