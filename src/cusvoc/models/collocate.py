from peewee import CharField
import os, sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.dynamic_model import DynamicModel



class Collocate(DynamicModel):

    collocate = CharField(unique=True)