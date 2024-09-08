from models.collocate import Collocate
from language import COLLOCATES


def seed_collocates():

    
    # Collocate.bulk_create([Collocate(collocate=collocate) for collocate in COLLOCATES])
    Collocate.insert_many([{'collocate': c} for c in COLLOCATES]).on_conflict_ignore().execute()
