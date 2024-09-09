"""
    This module provides functions and classes for handling lexical categories, sentences, and lexemes.

    Author: fimo_IT
    Version: 0.1.0
"""

__all__ = ['ARTICLES', 'COLLOCATES', 'SENTENCE_TERMINALS', 'is_singleword', 'is_sentence', 'GrammaticalCategory', 'LanguageSyntaxError']
__author__ = 'fimo_IT'
__version__ = '0.1.0'

import re
from enum import Enum


ARTICLES = ('the', 'a', 'an')
COLLOCATES = ('sb', 'sth', 'to sb', 'to sth', 'between sb', 'between sth', 'with sb', 'with sth', '<NOUN>', '<ADJECTIVE>', '<VERB>', '<ADVERB>') 
SENTENCE_TERMINALS = ('.', '?', '!')




def is_singleword(lexeme):
    return bool(re.fullmatch(r'[A-Za-z]+', lexeme))


def is_sentence(string: str):
    return string is not None and len(string) > 2 and string[0].isupper() and string[-1] in SENTENCE_TERMINALS



class GrammaticalCategory(Enum):
    NOUN = 1
    PRONOUN = 2
    VERB = 3
    ADJECTIVE = 4
    ADVERB = 5
    PREPOSITION = 6
    CONJUNCTION = 7
    INTERJECTION = 8
    PHRASAL_VERB = 9
    OPEN_COMPOUND = 10
    IDIOM = 11
    PHRASE = 12


class UsageLabel(Enum):
    FORMAL = 1
    INFORMAL = 2
    SLANG = 3
    BRITISH = 4
    AMERICAN = 5
    JARGON = 6
    LITERARY = 7
    ARCHAIC = 8
    VULGAR = 9





# @dataclass
# class WordDefinition():
    
#     string: str
#     lexical_category: LexicalCategory
#     collocate: str = None
#     sentence: str = None
    

#     def __post_init__(self):

#         # if self.prepositional_collocation is not None and self.prepositional_collocation not in PREPOSITIONAL_COLLOCATIONS:
#         #     raise LanguageSyntaxError(message="Provided string doesn't match any Prepositional Collocation.")

#         if self.sentence is not None and not is_sentence(self.sentence):
#             raise LanguageSyntaxError(message="Provided string breaks the sentence syntax.")





# class MissingPartOfSpeechError(Exception):
#     def __init__(self, lexeme):
#         super().__init__(f"The lexeme '{lexeme}' is a single word and not an article but has no part of speech assigned.")
#         self.lexeme = lexeme


class LanguageSyntaxError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)





# @dataclass
# class Lexeme():

#     lexeme: str
#     example_sentence: str = None
#     # part_of_speech: PartOfSpeech = None

#     definitions: List['WordDefinition'] = field(default_factory=list)
    

#     def __post_init__(self):
#         self.is_singleword = not is_singleword(self.lexeme)
        

#         for definition in self.definitions:
#             if (self.lexeme not in ARTICLES and definition.lexical_category is None and self.is_singleword):
#                 raise MissingPartOfSpeechError(lexeme=self.lexeme)
            




# @dataclass
# class Lexeme():

#     string: str



# @dataclass
# class SinglewordLexeme(Lexeme):

#     part_of_speech: PartOfSpeech

#     def __post_init__(self):
#         if not is_singleword(self.string):
#             raise LanguageSyntaxError("Provided string is not a single word!")
        
    



