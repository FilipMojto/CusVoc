from datetime import datetime
from peewee import CharField, BooleanField, ForeignKeyField, IntegerField, FloatField, DateTimeField


from models.dynamic_model import DynamicModel
from models.lexeme import Lexeme
from models.definition import Definition
from models.lexical_category import LexicalCategoryModel
from models.collocate import Collocate



class LexicalEntry(DynamicModel):
    lexeme = ForeignKeyField(Lexeme, backref='lexical_entries')
    definition = ForeignKeyField(Definition, backref='lexical_entries')
    lexical_category = ForeignKeyField(LexicalCategoryModel, backref='lexical_entries')
    collocate = ForeignKeyField(Collocate, backref='lexical_entries', null=True)

    sentence = CharField(null=True)

    # test fields
    test_count = IntegerField()
    for_practice = BooleanField()


    match_sum = FloatField()
    was_tested = BooleanField()
    was_practiced = BooleanField(null=True)
    
    created_at = DateTimeField()
    updated_at = DateTimeField()
    tested_at = DateTimeField(null=True)

    def save(self, *args, **kwargs):
        # If it's a new record, set created_at
        if not self.created_at:
            self.created_at = datetime.now()
        
        # Always set updated_at to current time
        self.updated_at = datetime.now()
        
        # handling for_practice and was_practiced
        if self.for_practice and self.was_practiced is None:
            self.was_practiced = False
        # If for_practice is False, set was_practiced to NULL
        elif not self.for_practice:
            self.was_practiced = None

        # Call the save method of the parent class
        return super(LexicalEntry, self).save(*args, **kwargs)
    

    # def test(self, match_ratio: float):
    #     self.was_tested = True
    #     self.test_count += 1
    #     self.tested_at = datetime.now()
