from language import GrammaticalCategory

from models.lexical_category import LexicalCategoryModel

def seed_lexical_categories():
    LexicalCategoryModel.insert_many([{'category': c.name} for c in GrammaticalCategory]).on_conflict_ignore().execute()

    
