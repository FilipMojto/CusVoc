
from peewee import CharField

from models.dynamic_model import DynamicModel


class Definition(DynamicModel):
    definition = CharField(unique=True)