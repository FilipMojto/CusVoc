# system libs
import os, sys

# external libs
from peewee import ForeignKeyField

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# package libs
from models.dynamic_model import DynamicModel
from models.lexical_entry import LexicalEntry
from models.usage_label import UsageLabelModel



class EntryLabel(DynamicModel):

	entry = ForeignKeyField(LexicalEntry, backref='entry_labels')
	label = ForeignKeyField(UsageLabelModel, backref='entry_labels')