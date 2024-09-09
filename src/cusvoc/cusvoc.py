"""
    This is the main script of CusVoc Application. In order to operate properly the following modules must be available:

    a) cusvoc.language
    b) all models from cusvoc.models package
    c) all seeds from cusvoc.seeds package
    d) cusvoc.vocabulary
    e) cusvoc.audiopron
    f) cusvoc.testvoc

    Author: fimo_IT
    Version: 0.2.0
"""



__author__ = 'fimo_IT'
__version__ = '0.2.0'





from enum import Enum
import argparse
import csv
import os

from vocabulary import Vocabulary
from audiopron import PhoneticsAudioManager
from language import GrammaticalCategory, UsageLabel


# DEF_DB_PATH = '../../data/vocabulary.db'

# ensures that DEF_DB_PATH is always relative to the location of the script file,
# not the directory from which the script is run.

## CONSTANTS 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEF_DB_PATH = os.path.join(BASE_DIR, '../../data/vocabulary.db')

PUBLIC_DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/" # append a word here to get its data

## ENTRY FILES


DEF_IMPORT_FILE_PATH =  os.path.join(BASE_DIR, '../../data/imports/vocabulary.tsv')
DEF_EXPORT_FILE_PATH =  os.path.join(BASE_DIR, '../../data/exports/vocabulary.tsv')
DEF_FILE_DELIMITER = '\t'

class EFF(Enum):
    """
        EFF stands for Entry File Field
    """
    ID = 'ID'
    lexeme = 'lexeme'
    definition = 'definition'
    lexical_category = 'lexical_category'
    collocate = 'collocate'
    sentence = 'sentence'
    for_practice = 'for_practice'
    pac_file = 'pac_file'

ENTRY_FILE_FIELDS = [field.value for field in EFF]






def import_entries(vocabulary: Vocabulary, audio_manager: PhoneticsAudioManager, f_path: str = DEF_IMPORT_FILE_PATH):
    from cuslog import FunctionLogger

    with open(file=f_path, mode='r', encoding='utf-8') as src_file:
        
        # Create a CSV DictReader with the correct delimiter
        reader = csv.DictReader(src_file, delimiter=args.delimiter, fieldnames=ENTRY_FILE_FIELDS)
        
        next(reader)
        
        # Iterate over each row in the CSV
        for row in reader:
            # print(vocabulary.__str__())
            # print(row)

            FunctionLogger.execute(fun=lambda: vocabulary.create_lexical_entry(
                    lexeme=row[EFF.lexeme.value],
                    definition=row[EFF.definition.value],
                    category=GrammaticalCategory[row[EFF.lexical_category.value]],
                    collocate=row[EFF.collocate.value] if row[EFF.collocate.value] else None,
                    sentence=row[EFF.sentence.value] if row[EFF.sentence.value] else None,
                    for_practice=bool(int(row[EFF.for_practice.value])) if row[EFF.for_practice.value] else False
                ), end_msg="Operation successful!", exception_msg="Operation unsuccessful:", exception=Exception)#, exception=Exception, exception_msg="Operation unsuccessful: ")

            # try:
            #     vocabulary.create_lexical_entry(
            #         lexeme=row[EFF.lexeme.value],
            #         definition=row[EFF.definition.value],
            #         category=GrammaticalCategory[row[EFF.lexical_category.value]],
            #         collocate=row[EFF.collocate.value] if row[EFF.collocate.value] else None,
            #         sentence=row[EFF.sentence.value] if row[EFF.sentence.value] else None,
            #         for_practice=bool(int(row[EFF.for_practice.value])) if row[EFF.for_practice.value] else False
            #     )
            # except Exception as e:
            #     raise e
            
            # PAC files are automatically created if required
            if row['pac_file'] and int(row['pac_file']):
                audio_manager.create_PAC(lexeme_identifier=row['lexeme'])



def export_entries(vocabulary: Vocabulary, f_path: str = DEF_EXPORT_FILE_PATH):

    # file contains some content
    if os.path.exists(f_path) and os.stat(f_path).st_size:
        
        while True:
            print("Provided file contains some content. Still continue? (y/n):", end=" ")
            response = input()

            if response == 'y':
                break
            elif response == 'n':
                return
        
    with open(file=f_path, mode='w', encoding='utf-8', newline="") as src_file:
        writer = csv.DictWriter(f=src_file, fieldnames=ENTRY_FILE_FIELDS, delimiter=args.delimiter)
        writer.writeheader()
        entries = vocabulary.__lexical_entry__(filter=None, to_list=True)

        for index, entry in enumerate(entries, start=1):
            writer.writerow({
                EFF.ID.value : entry.id,
                EFF.lexeme.value : entry.lexeme.string,
                EFF.definition.value : entry.definition.definition,
                EFF.lexical_category.value : entry.lexical_category.category,
                EFF.collocate.value : entry.collocate.collocate if entry.collocate else "",
                EFF.sentence.value : entry.sentence,
                EFF.for_practice.value : int(entry.for_practice),
                EFF.pac_file.value : 1 if entry.lexeme.PAC_file_path else 0
            })
            

        

# part_of_speech_choices = []

# for POS in GrammaticalCategory:
#     part_of_speech_choices.append(POS.name)

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog='CusVocApp',
        description='Welcome to the CusVoc App! This script helps you manage your personal vocabulary. You can add new words manually, or use a public dictionary API for faster input.',
    # CusVoc also provides test mechanisms to help you memorize the words more effectively.',
        epilog="""
        EXAPLANATIONS

            a) Lexeme - Includes anything ranging from a single words (e.g. drink, apple, on, etc.) to multiword (composite) lexemes (e.g. phrasal verbs, phrases, etc.)
            b) Lexical Entry - Represents a specific word instance in vocabulary, which includes a lexeme, its category, definition and, optionally, a sentence and collocate.


        USAGE EXAMPLES
            - Filter by column: --where "word LIKE 'apple%'
            - Add a new entry: -a -le apple -d "A fruit" -c noun
            - Remove an entry: -r -le 42

        """
        )



# CusVoc Command Set


## General Commands
parser.add_argument('-db', '--database', metavar='PATH', nargs=1, default=DEF_DB_PATH, help="Sets the provided value as a relative path of the source database file.")
parser.add_argument('-v', '--vocabulary', action='store_true', help="Prints vocabulary metadata to the console.")



## Lexical Entry Command Set

parser.add_argument('-e', '--entry', metavar='ID', nargs="*", help="If no arguments are provided, '--where' is expected. If provided, args are joined and entry is searched by id if joined args are digit, otherwise by string.")
parser.add_argument('-c', '--create', action='store_true', help="Serves as a flag to indicate that the entry will be inserted into database.")

### alternative 1: adding entry manually via Console
parser.add_argument('-d', '--definition', nargs="+", help="Uses the value as a definition when for instance when appending an entry.")
parser.add_argument('-ctg', '--lexical-category', choices=[c.name for c in GrammaticalCategory], help="Uses the value as a lexical category for instance when appending an entry.")
parser.add_argument('--label', nargs="*", choices=[l.name for l in UsageLabel], help="Requires one or more strings representing Label(s) Of Usage within the entry.")
parser.add_argument('-col', '--collocate', nargs="*", help="Uses the value as a collocate for instance when appending an entry.")
parser.add_argument('-s', '--sentence', nargs="*", help="Uses the value as a sentence linked for example to a particular entry.")

# parser.add_argument('--practice', action='store_true', help="If provided, created entry is is set for practice.")


### alternative 2: adding definition(s) via file
parser.add_argument('--import-file', metavar='PATH', nargs="*", help="Loads entries from a source file (formats .tsv, .csv etc.). If no argument is provided, default path is used.")
parser.add_argument('--export-file', metavar='PATH', nargs="*")

parser.add_argument('--delimiter', nargs=1, metavar='DELIMITER', default=DEF_FILE_DELIMITER, help=f"Uses the value as a delimiter for a file, default value is a tab.")

### filtering lexical entries
parser.add_argument('--where', nargs=1, metavar='"<COL> <OPERATOR> <VAL>"', required=False,
                    help=f"Filter entries where a condition is met. Available fields: {', '.join(Vocabulary.EntryFilter.FIELDS)}. Available operators: {', '.join(Vocabulary.Filter.OPERATORS)}")
                    # help=f"""Filter entries where a condition is met. Available columns: {', '.join(valid_columns)}. Available operators: {', '.join(valid_operators)}. Example: --where \"word LIKE 'app%'\"""")


## Lexeme Command Set

parser.add_argument('-l', '--lexeme', nargs="*", help="If no arguments are provided, '--where' is expected. If provided, args are joined and lexeme is searched by id if the args are digit, otherwise by string.")
parser.add_argument('-p', '--pronunciation', action='store_true', help="Use with '-l'. If used along with -a, stores the audio locally, otherwise only plays from API.")
# parser.add_argument('-api', action='store_true')


## Shared Command Set

parser.add_argument('-all', action='store_true', help="When true, script prints all lexemes or entries and their metadata to console in tabular form.")
parser.add_argument('-r', '--remove', action='store_true', help="Flag indicates user's intetion to remove a lexeme or entry from database.")


# Testing Command Set

parser.add_argument("-t", '--test', nargs=1, metavar='N', type=int, help="Expects an integer representing the number of tested entries in a single test.")
parser.add_argument('--practice', nargs="*", metavar=' | N | N%', help="Integer represents number of allocated for-practice entries, if '%%' is appended, this represents proportion.")





args = parser.parse_args()

if args.delimiter is None:
    args.delimiter = DEF_FILE_DELIMITER


# Custom validation logic
# if (args.create or args.remove) and (args.lexeme_entry is None and args.definition is None):
#     parser.error("The '-a' (append) and '-r' (remove) flags can only be used in combination with the '-l' (lexeme) and '-d' (definition) arguments.")
# elif (args.lexical_category is not None or args.collocate is not None or args.sentence is not None or args.file is not None or args.delimiter is not None) and (args.lexeme_entry is None or not args.create):
#     parser.error("The '-d' (definition), '-lt' (lexical-category), '-col' (collocate) and '-s' (sentence) flags can only be used in combination with the '-l' (lexeme) and '-a' (append) arguments.")
# elif (not args.vocabulary and args.lexeme_entry):
#     parser.error("The '-l' can only be used as a flag in combination with '-v' argument.")
# elif (args.definition or args.part_of_speech or args.prepositional_collocation or args.sentence) and (args.file or args.delimiter):
#     parser.error("Arguments '-d', '-pos', '-pc' and '-s' cannot be used along with '-f' or '-de' arguments.")


# validation of adding a new definition to a lexeme
# 2 approaches available:
#   a) adding a single definition via terminal (combination of -d, -pos, -pcol and -s arguments)
#   b) adding a batch of definitions via an external file (combination of -f and (optionally)-d arguments)

# elif args.lexeme_entry and args.create and ( ((args.definition or args.lexical_category or args.collocate or args.sentence)  or
#                                        (not args.definition and not args.lexical_category and not args.file and not args.pronunciation) ):
#     parser.error("Incompatible use of -a command's arguments.")







def main():

    from typing import List
    from prettytable import PrettyTable
    from pathlib import Path
    import os


    from language import GrammaticalCategory
    from vocabulary import Vocabulary, Lexeme

    from testvoc import Tester, TestQuestion
    from audiopron import PhoneticsAudioManager, extract_audio_content_from_api, play_temp_audio_file
    from cuslog import FunctionLogger


    base_dir = Path.home()
    app_dir = None

    if os.name == 'nt':  # Windows
        app_dir = base_dir / 'AppData' / 'Local' / 'CusVoc'
    else:  # macOS/Linux
        app_dir = base_dir / '.cusvoc'

    app_dir.mkdir(parents=True, exist_ok=True)

    os.makedirs(name=app_dir.__str__() + '/audio/', exist_ok=True, )
    # os.mk
    os.makedirs(name=app_dir.__str__() + '/audio/PAC_files/', exist_ok=True)


    # def create_lexeme_entry(lexeme: str, definition: str, category: GrammaticalCategory, collocate: str = None, sentence: str = None, for_practice: bool = False):

    #     try:
    #         # vocabulary.create_lexical_entry(lexeme=lexeme)

    #         vocabulary.create_lexical_entry(lexeme=lexeme,
    #                                         definition=definition,
    #                                         category=category,
    #                                         collocate=collocate,
    #                                         sentence=sentence,
    #                                         for_practice=for_practice)
            
    #         print("Operation successful!")

    #     except Exception as e:
      
    #         print(f"Operation unsuccessful: {e}")


    

    vocabulary = Vocabulary(db_file_path=args.database)
    database = vocabulary.database()

    tester = Tester(vocabulary=vocabulary)
    audio_manager = PhoneticsAudioManager(vocabulary=vocabulary, PAC_dir=app_dir.__str__() + '/audio/PAC_files/')

    def process_where_args(args: str):
        for operator in Vocabulary.Filter.OPERATORS:
            sep = " " + operator + " "

            if sep in args:
                return args.split(sep=sep) + [operator]
        else:
            print("Unsupported!")

                
    

    if args.lexeme is not None:
        lexeme = " ".join(args.lexeme)


        if args.remove:
            try:
                vocabulary.delete_lexeme(string=lexeme)
                print("Operation successful!")
            except Exception as e:
                print(f"Operation unsuccessful: {e}")
        
        elif args.all:
            print(vocabulary.__lexeme__(filter=None))

        elif args.pronunciation:

            if args.create:
                if not audio_manager.create_PAC(lexeme_identifier=lexeme):
                    print("The lexeme has already a Pronunciation Clip assigned!")
                else:
                    print("Pronunciation Clip created successfully!")
            elif args.remove:
                if audio_manager.delete_PAC(lexeme_identifier=lexeme):
                    print("Pronunciation Clip removed successfully!")    
                else:
                    print("The lexeme doesn't have any Pronunciation Clip assigned!")
                    
            else:

                if not audio_manager.play_PAC(lexeme_identifier=lexeme):
                    
                    if lexeme.isdigit():
                        lexeme = Lexeme.get(Lexeme.id == lexeme).string


                    content = extract_audio_content_from_api(lexeme=lexeme)
                    play_temp_audio_file(content=content)
        
        elif args.where:
            where_args = process_where_args(args=args.where[0])

            print(vocabulary.__lexeme__(filter=Vocabulary.LexemeFilter(field=where_args[0], value=where_args[1], operator=where_args[2])))

        else:
            print(vocabulary.__lexeme__(Vocabulary.LexemeFilter(field='id' if lexeme.isdecimal() else 'string', operator='==', value=lexeme)))



    elif args.entry is not None:
        lexeme = " ".join(args.entry)
 
        if args.create:
            
            FunctionLogger.execute(fun=vocabulary.create_lexical_entry(
                    lexeme=lexeme,
                    definition=" ".join(args.definition),
                    category=GrammaticalCategory[args.lexical_category],
                    usage_labels=[UsageLabel[l] for l in args.label] if args.label else None,
                    collocate=" ".join(args.collocate) if args.collocate else None,
                    sentence=" ".join(args.sentence) if args.sentence else None,
                    for_practice=True if not args.practice else False
                ), exception=Exception, end_msg="Operation Successful!", exception_msg="Operation unsuccessful: ")

            # try:
            #     vocabulary.create_lexical_entry(
            #         lexeme=lexeme,
            #         definition=" ".join(args.definition),
            #         category=GrammaticalCategory[args.lexical_category],
            #         usage_labels=[UsageLabel[l] for l in args.label] if args.label else None,
            #         collocate=" ".join(args.collocate) if args.collocate else None,
            #         sentence=" ".join(args.sentence) if args.sentence else None,
            #         for_practice=True if not args.practice else False
            #     )
            # except Exception as e:
            #     raise e

            # # else:
            # create_lexeme_entry(lexeme=lexical_entry,
            #                     definition=" ".join(args.definition),
            #                     category=GrammaticalCategory[args.lexical_category],
            #                     collocate=" ".join(args.collocate) if args.collocate else None,
            #                     sentence=" ".join(args.sentence) if args.sentence else None,
            #                     for_practice=True if len(args.practice) == 0 else False)


                
        elif args.remove:
            pass
  
        
        elif args.all:
            print(vocabulary.__lexical_entry__(filter=None))

        elif args.where:
            where_args = process_where_args(args=args.where[0])
            print(vocabulary.__lexical_entry__(filter=Vocabulary.EntryFilter(field=where_args[0], value=where_args[1], operator=where_args[2])))

        else:
            
            if lexeme.isdigit():
                print(vocabulary.__lexical_entry__(filter=Vocabulary.EntryFilter(field='id', operator='==', value=lexeme)))
            else:
                print(vocabulary.__lexical_entry__(filter=Vocabulary.EntryFilter(field='definition', operator='==', value=lexeme)))
    
    elif args.import_file is not None:
        import_entries(f_path=args.import_file[0] if args.import_file else DEF_IMPORT_FILE_PATH, audio_manager=audio_manager, vocabulary=vocabulary)


    elif args.export_file is not None:
        export_entries(f_path=args.export_file[0] if args.export_file else DEF_EXPORT_FILE_PATH, vocabulary=vocabulary)
   
    elif args.definition:

        if args.remove:
            vocabulary.delete_definition(ID=int(args.definition[0]))
    
    elif args.label is not None and not args.label and args.all:
        print(vocabulary.__labels__(to_list=False))



    elif args.vocabulary:

        if args.entry is None:
            print(vocabulary.__str__())
        elif not args.entry:
            vocabulary.__lexemes__()
    
    elif args.test:
        
        if args.practice is not None:
            practice_val = args.practice[0]

            if practice_val[-1] == '%':
                value = int(practice_val[:-1])
                mode = 'percentage'
            elif practice_val.isdigit():
                value = int(args.practice)
                mode = 'count'
            else:
                print("Invalid")
        else:
            value = 0
            mode=None

        
        questions: List[TestQuestion] = tester.test_vocabulary(number_of_tests=args.test[0], for_practice=value, practice_mode=mode)

        if not questions:
            print("No words in dictionary! At least 1 required for testing.\n")
        
        else:
            print("Assign correct lexemes to the following definitions: ", end="\n\n")

            for index, question in enumerate(questions):
                table = PrettyTable(field_names=['Expected Answer', 'Results', 'Sentence'])

                print(f'{index + 1}. "{str(question.ask())}": ', end="")

                question.answer(lexeme=input(""))

                print("\nTEST RESULTS")
                entry = tester.submit_question(question=question)
                
                table.add_row([question.get_answer(), str(question.get_evaluation()) + "%", entry.sentence])
                print(table)
                print()

    else:
        print("Welcom to CusVoc Terminal. Use -h for printing help.")
        
    print("Program terminated successfully!\n")

    if database is not None and not database.is_closed():
        database.close()




if __name__ == '__main__':
    main()