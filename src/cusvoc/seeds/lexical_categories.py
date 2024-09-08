from language import LexicalCategory

from models.lexical_category import LexicalCategoryModel

def seed_lexical_categories():
    LexicalCategoryModel.insert_many([{'category': c.name} for c in LexicalCategory]).on_conflict_ignore().execute()

    
