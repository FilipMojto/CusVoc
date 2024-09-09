# SYSTEM LIBS
import os, sys


# PACKAGE LIBS
from models.usage_label import UsageLabelModel
from language import UsageLabel


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def seed_usage_labels():
	UsageLabelModel.insert_many([{'label': l.name} for l in UsageLabel]).on_conflict_ignore().execute()