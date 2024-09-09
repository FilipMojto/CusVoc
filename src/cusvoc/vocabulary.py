# --- SYSTEM LIBS ---

from typing import List, Literal, Iterable
from dataclasses import dataclass

import os
import time

from sqlite3 import IntegrityError

# --- EXTERNAL LIBS ---

from prettytable import PrettyTable
from peewee import *

# --- PACKAGE LIBS ---

from language import GrammaticalCategory, LanguageSyntaxError, is_sentence, UsageLabel

from seeds.collocates import seed_collocates
from seeds.lexical_categories import seed_lexical_categories
from seeds.usage_labels import seed_usage_labels

from models.collocate import Collocate
from models.definition import Definition
from models.lexeme import Lexeme
from models.lexical_category import LexicalCategoryModel
from models.lexical_entry import LexicalEntry
from models.usage_label import UsageLabelModel
from models.entry_label import EntryLabel



# --- EXCEPTIONS ---
class ContraintViolationError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class LexemeNotFoundError(Exception):
    pass


class LexicalEntryNotFound(Exception):
    pass






class Vocabulary():
    """
        Vocabulary represents a public API available for users which provides all CRUD operations for an effective maintenance of a Personal Vocabulary.

        Data are stored locally via Sqlite Relational Database System. 
    """

    MAX_SENTENCE_CHAR_COUNT = 100
    PUBLIC_DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/" # append a word here to get its data



    def __init__(self, db_file_path: str) -> None:

        """
            Initializes a new Vocabulary Instance dependent on the provided sqlite3 Connection Instance and with the provided name.

            A new Vocabulary Instance automatically reserves a new Cursor Instance from the Connection Instance.
            Predefined Database Schema for CusVoc Application is also automatically imported if not present.
            Tables lexeme_types and collocates are automatically seeded if not present.
        """
        
        # --- CONFIGURING DATABASE --- #
        self.name = os.path.basename(db_file_path)

        self.db_file_path = db_file_path
        self.__database = SqliteDatabase(db_file_path)
        
        # --- IMPORTING MODELS --- #
        Lexeme.connect_db(db=self.__database, table_name='lexemes')
        Collocate.connect_db(db=self.__database, table_name='collocates')        
        Definition.connect_db(db=self.__database, table_name='definitions')
        LexicalCategoryModel.connect_db(db=self.__database, table_name='lexical_categories')
        LexicalEntry.connect_db(db=self.__database, table_name='lexical_entries')
        UsageLabelModel.connect_db(db=self.__database, table_name='usage_labels')
        EntryLabel.connect_db(db=self.__database, table_name='entry_labels')


        self.__database.connect()
        self.__database.create_tables([Lexeme, Collocate, Definition, LexicalCategoryModel, LexicalEntry, UsageLabelModel, EntryLabel])


        # --- SEEDING DATA --- #

        seed_lexical_categories()
        seed_collocates()
        seed_usage_labels()
        


    def __str__(self):
        
        return f'Vocabulary::Name={self.name}, Lexemes={self.lexeme_count()}, Lexical Entries={self.lexical_entry_count()}'


    def __labels__(self, to_list: bool = False):

        entry_buffer: PrettyTable | List[UsageLabelModel] = PrettyTable(field_names=['No.', 'Label']) if not to_list else []
        entries: Iterable[UsageLabelModel] = UsageLabelModel.select(UsageLabelModel.label)

        if to_list:
            return list(entry_buffer)
        else:
            for index, entry in enumerate(entries, 1):
                entry_buffer.add_row([index, entry.label])
            
        return entry_buffer




    def create_lexical_entry(self, lexeme: str, definition: str, category: GrammaticalCategory, usage_labels:  UsageLabel | Iterable[UsageLabel] = None, collocate: str = None, sentence: str = None, for_practice: bool = False):
        """_summary_

        Args:
            lexeme (str): _descrisption_
            definition (str): _description_
            category (LexicalCategory): _description_
            collocate (str, optional): _description_. Defaults to None.
            sentence (str, optional): _description_. Defaults to None.
            for_practice (bool, optional): _description_. Defaults to False.

        Raises:
            LanguageSyntaxError: Provided argument breaks the sentence format. For more info see _is_sentece()_ function from _language_ module.
            ContraintViolationError: Provided argument exceeds the maximum limit of sentence characters. Check _MAX_SENTENCE_CHAR_COUNT_ variable.
            IntegrityError: 
        """
        # try:
        if not is_sentence(string=sentence):
            raise LanguageSyntaxError(message="Argument 'sentence' is not a sentence!")
        
        
        if sentence and len(sentence) > self.MAX_SENTENCE_CHAR_COUNT:
            raise ContraintViolationError(message="Provided sentence exceeds maximum limit of characters.")


        with self.__database.atomic() as transaction:
            try:
                lexeme_model: Lexeme = Lexeme.get_or_none(Lexeme.string == lexeme)
                found_lexeme_flag: bool = False

                if lexeme_model is None:
                    lexeme_model = Lexeme.create(string=lexeme, example_sentence=None, PAC_file_path=None)
                    lexeme_model.save()
                else:
                    found_lexeme_flag = True

                definition_model: Definition = Definition.get_or_none(Definition.definition == definition)

                if definition_model is None:
                    definition_model = Definition.create(definition=definition)
                    definition_model.save()
                elif found_lexeme_flag and LexicalEntry.get_or_none(LexicalEntry.lexeme.id == lexeme_model.get_id() and
                                                                    LexicalEntry.definition == definition_model.get_id()) is not None:
                        
                        raise IntegrityError("Instance with same lexeme and definition already in database!")
                    

                
                lexical_category_model: LexicalCategoryModel = LexicalCategoryModel.get(LexicalCategoryModel.category == category.name)



                if collocate:
                    collocate_model: Collocate = Collocate.get_or_none(Collocate.collocate == collocate)

                    if collocate_model is None:
                        collocate_model = Collocate.create(collocate=collocate)
                        collocate_model.save()


                lexical_entry: LexicalEntry = LexicalEntry.create(lexeme=lexeme_model.get_id(),
                                                                    definition=definition_model.get_id(),
                                                                    lexical_category=lexical_category_model.get_id(),
                                                                    collocate=collocate_model.get_id() if collocate else None,
                                                                    
                                                                    sentence=sentence,
                                                                    test_count=0,
                                                                    was_tested=False,
                                                                    match_sum=0,
                                                                    for_practice=for_practice)

                lexical_entry.save()



                if usage_labels is not None:
                    if isinstance(usage_labels, UsageLabel):
                        usage_labels = list(usage_labels)
                    
                    if isinstance(usage_labels, Iterable):
                        for label in usage_labels:
                            # usage_label = UsageLabelModel.get_by_id(label.value)
                            EntryLabel.create(entry=lexical_entry, label=UsageLabelModel.get_by_id(label.value)).save()
                        

                    else:
                        raise TypeError("Argument usage_labels must be an iterable!")
            except Exception as e:
                transaction.rollback()
                raise e

                


        
    def database(self):
        return self.__database

    def lexeme_count(self):
        return Lexeme.select().count()

    def lexical_entry_count(self):
        """
            Returns a total count of Lexical Entries present in the current database.
        """

        return LexicalEntry.select().count()


    

    def __insert_lexical_entry_to_table(self, table: PrettyTable, entry: LexicalEntry, index: int):
        
        definition: Definition = entry.definition
        l_category: LexicalCategoryModel = entry.lexical_category
        collocate: Collocate = entry.collocate

        table.add_row([
            index, 
            entry.id,  # Use entry.id directly
            '"' + definition.definition + '"', 
            l_category.category, 
            collocate.collocate if collocate is not None else '---', 
            entry.sentence, 
            entry.test_count, 
            str( round((entry.match_sum / entry.test_count) * 100, 2) if entry.test_count else 0) + '%', 
            entry.for_practice,
            ", ".join([entry_label.label.label for entry_label in entry.entry_labels])
        ])

    
    @dataclass
    class Filter():
        OPERATORS = [">", '>=', '<', '<=', '==', '!=', 'LIKE']

        operator: str
        value: str | int | float | bool | None

        def __post_init__(self):
            if self.operator not in self.OPERATORS:
                raise ValueError("Unsupported operator!")
            



    @dataclass
    class LexemeFilter(Filter):
        field: Literal['string', 'PAC_saved', 'entry_count']


    def __lexeme__(self, filter: LexemeFilter = None):
        """
        This method pretty-prints a word and its attributes to the console.
        """

        table = PrettyTable(field_names=['No.', 'ID', 'Lexeme', 'Entry Count', 'PAC_saved'])
        query = (Lexeme.select(Lexeme, fn.COUNT(LexicalEntry.id).alias('entry_count'))
                    .join(LexicalEntry, JOIN.LEFT_OUTER)
                    .group_by(Lexeme))
        
        if filter is not None:
            if filter.field != 'entry_count':
                query = query.where(self.compare(val_1=getattr(Lexeme, filter.field), operator=filter.operator, val_2=self.parse_value(filter.value)))
        
        lexemes = query.execute()


        
        for idx, entry in enumerate(lexemes, start=1):
            table.add_row([idx, entry.id, entry.string, entry.entry_count, True if entry.PAC_file_path else False])

        return table
     


    def __lexemes__(self):

        lexemes: List[Lexeme] = Lexeme.select()

        table = PrettyTable()
        table.field_names = ['No.', 'Lexeme', 'Lexical Entries', 'Total Tests', 'Total Match Sum', 'Average Match Rate']

        query = (
            Lexeme
            .select(
                Lexeme, 
                fn.COUNT(LexicalEntry.id).alias('le_count'), 
                fn.SUM(LexicalEntry.test_count).alias('total_test_count'),
                fn.SUM(LexicalEntry.match_sum).alias('match_sum'),
                Case(
                    None,  # No specific field, we're working with aggregates
                    (
                        (fn.SUM(LexicalEntry.test_count) == 0, '---'),  # If test_count is 0, return '---'
                    ),
                    (fn.SUM(LexicalEntry.match_sum) / fn.SUM(LexicalEntry.test_count))  # Else calculate average
                ).alias('average_match_rate')
            )
            .join(LexicalEntry, JOIN.LEFT_OUTER)
            .group_by(Lexeme)
        )

        for index, lexeme_metadata in enumerate(query):
            table.add_row([index + 1, lexeme_metadata.string, lexeme_metadata.le_count, lexeme_metadata.total_test_count, lexeme_metadata.match_sum,
                           lexeme_metadata.average_match_rate])
        
        return f"\n{table}\n"



    def compare(self, val_1: object, val_2, operator: Literal['>', '>=', '<', '<=', '==', '!=', 'LIKE']):
    
        match operator:
            case '>':
                return val_1 > val_2
            case '>=':
                return val_1 >= val_2
            case '<':
                return val_1 < val_2
            case '<=':
                return val_1 <= val_2
            case '==':
                return val_1 == val_2
            case '!=':
                return val_1 != val_2
            case 'LIKE':
                return val_1 ** val_2

            case _:
                raise ValueError('Unknown operator provided!')
            


    def parse_value(self, value: str):
        # Check for special values and cast them to the correct type
        special_values = {
            "True": True,
            "False": False,
            "None": None,
        }

        # Handle numbers (integers and floats)
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Handle special values
        if value in special_values:
            return special_values[value]

        # Handle values wrapped in double quotes
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]  # Return value without the surrounding quotes

        # If no special condition matches, treat it as a string
        return value
        


    # FIELDS = ['id', 'lexeme', 'definition', 'category', 'collocate', 'test_count', 'was_tested', 'for_practice', 'label']

    @dataclass
    class EntryFilter(Filter):
        from enum import Enum

        

        class Field(Enum):

            id = 1
            lexeme = 2
            definition = 3
            category = 4
            collocate = 5
            test_count = 6
            was_tested = 7
            for_practice = 8
            labels = 9

        FIELDS = [field.name for field in Field]

        field: Field

        
        


    def __lexical_entry__(self, filter: EntryFilter = None, to_list: bool = False):
        # start = time.time()
        
        

        if to_list:
            entry_list: List[LexicalEntry] = []
        else:
            # print(Vocabulary.EntryFilter.FIELDS)
            table = PrettyTable(field_names=['No.'] + Vocabulary.EntryFilter.FIELDS)
        

        # Construct the query
        query = LexicalEntry.select().join(Lexeme).switch(LexicalEntry).join(Definition).switch(LexicalEntry).join(LexicalCategoryModel)

        if filter is not None:
            if filter.field == 'lexeme':
                related_field = Lexeme.string
            elif filter.field == 'definition':
                related_field = Definition.definition
            elif filter.field == 'category':
                related_field = LexicalCategoryModel.category
            elif filter.field == 'collocate':
                related_field = Collocate.collocate
            else:
                related_field = getattr(LexicalEntry, filter.field)

            # Apply the filter using the compare function
            query = query.where(self.compare(val_1=related_field, val_2=filter.value, operator=filter.operator))

        # Execute the query and iterate over the results
        entries = query.execute()


        

        # Insert entries into the table
        for idx, entry in enumerate(entries, start=1):
            if to_list:
                entry_list.append(entry)
            else:
                self.__insert_lexical_entry_to_table(table=table, entry=entry, index=idx)

        # end = time.time()

        # print(end - start)

        return entry_list if to_list else table




    def delete_lexeme(self, string: str):
        self.__cursor.execute('DELETE FROM lexemes WHERE string == (?)', (string, ))

        # user cannot remove multiple words
        assert(self.__cursor.rowcount <= 1)

        print("Lexeme removed successfully!\n") if self.__cursor.rowcount == 1 else print("Lexeme not found!\n")


        self.__conn.commit()

    
    def delete_definition(self, ID: int):
        self.__cursor.execute('DELETE FROM definitions WHERE id = ?', (ID, ))

        # user cannot remove multiple definitions
        assert(self.__cursor.rowcount <= 1)

        print("Definition removed successfully!\n") if self.__cursor.rowcount == 1 else print("Definition not found!\n")

        self.__conn.commit()
    
