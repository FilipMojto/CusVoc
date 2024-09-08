from peewee import CharField

from models.dynamic_model import DynamicModel



class LexicalCategoryModel(DynamicModel):
    category = CharField(unique=True)