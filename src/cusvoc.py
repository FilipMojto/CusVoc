
# import random
import argparse
import csv
import sqlite3
from typing import List
from prettytable import PrettyTable
import os
# import shutil
# from pathlib import Path
# from platformdirs import user_data_dir, user_cache_dir, user_config_dir

from language import Lexeme, LexemeType, WordDefinition
from vocabulary import Vocabulary
from testvoc import Tester, TestQuestion


DEF_DB_PATH = '../data/vocabulary.db'
DEF_FILE_DELIMITER = '\t'


# def get_backup_directory(app_name: str) -> Path:
#     """
#     Returns a safe cross-platform directory for storing backups.
    
#     app_name: The name of your application. This will be used to create a subdirectory.
#     """
#     backup_dir = Path(user_data_dir(app_name)) / "backups"
#     backup_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
#     return backup_dir

# def backup_db(source_db: Path, app_name: str) -> None:
#     """
#     Backs up the database to a safe location in the user's data directory.
    
#     source_db: The path to the source database file.
#     app_name: The name of your application.
#     """
#     backup_dir = get_backup_directory(app_name)
#     backup_file = backup_dir / f"{source_db.stem}_backup{source_db.suffix}"
    
#     # Copy the database file to the backup location
#     shutil.copy2(source_db, backup_file)
#     print(f'Backup created at: {backup_file}')


# def get_backup_file(app_name: str) -> Path:
#     """
#     Retrieve the latest backup file path.
    
#     app_name: The name of your application.
#     """
#     backup_dir = get_backup_directory(app_name)
#     backups = list(backup_dir.glob("*.db"))
#     return max(backups, key=os.path.getctime) if backups else None



part_of_speech_choices = []

for POS in LexemeType:
    part_of_speech_choices.append(POS.name)

parser = argparse.ArgumentParser(
        prog='CusVocApp',
        description='Welcome to the CusVoc App! This script helps you manage your personal vocabulary. You can add new words manually, or use a public dictionary API for faster input.',
    # CusVoc also provides test mechanisms to help you memorize the words more effectively.',
        epilog="A Lexeme can be anything from single-word lexemes (drink, apple, on) to multiword (composite) lexemes (e.g phrasal verbs, open compounds, or idioms).\n Use '-a' and '-r' in combination with '-l' command.")    

# Vocabulary Command Set

parser.add_argument('-db', '--database', required=False, help="Uses the value as a custom name for database.")
parser.add_argument('-v', '--vocabulary', required=False, action='store_true', help="Prints vocabulary metadata into the console.")




# Lexeme Command Set

parser.add_argument('-l', '--lexeme', required=False, nargs="*", help="Uses the value to search for the lexeme by its string a prints its metadata to the console.")
parser.add_argument('-a', '--append', action='store_true', help="Serves a flag to indicate that the lexeme will be inserted into database.")

# alternative 1: adding definition manually via Console
parser.add_argument('-d', '--definition', nargs="*", help="Uses the value as a Definition of a referenced lexeme.")
parser.add_argument('-pos', '--part-of-speech', choices=part_of_speech_choices, help="Uses the value as a Part-of-Speech of the referenced lexeme.")
parser.add_argument('-pcol', '--prepositional-collocation', nargs="*", help="Uses the value as a Prepositonal Collocation of the referenced lexeme.")
parser.add_argument('-s', '--sentence', nargs="*", help="Uses the value as a Sentence containing the referenced lexeme and in the context of the provided definiton.")

# alternative 2: adding definition(s) via file
parser.add_argument('-f', '--file', help="Uses the value as a Path to file containing Definition Metadata.")
parser.add_argument('-de', '--delimiter', help="Uses the value as a Custom File Delimiter.")

# alternative 3: printing all definitions

parser.add_argument('-all', action='store_true', help="When true, prints all definitions and their metadata to console using in a table format.")

parser.add_argument('-r', '--remove', action='store_true')


# Testing Command Set

parser.add_argument("-t", '--test', required=False, type=int)

















# parser.add_argument('filename')           # positional argument
# parser.add_argument('-c', '--count')      # option that takes a value
# parser.add_argument('-v', '--verbose',
#                     action='store_true')  # on/off flag

args = parser.parse_args()


# Custom validation logic
if (args.append or args.remove) and (args.lexeme is None and args.definition is None):
    parser.error("The '-a' (append) and '-r' (remove) flags can only be used in combination with the '-l' (lexeme) and '-d' (definition) arguments.")
elif (args.part_of_speech is not None or args.prepositional_collocation is not None or args.sentence is not None or args.file is not None or args.delimiter is not None) and (args.lexeme is None or not args.append):
    parser.error("The '-d' (definition), '-pos' (part-of-speech), '-pc' (prepositional-collocation) and '-s' (sentence) flags can only be used in combination with the '-l' (lexeme) and '-a' (append) arguments.")
# elif (not args.vocabulary and args.lexeme):
#     parser.error("The '-l' can only be used as a flag in combination with '-v' argument.")
# elif (args.definition or args.part_of_speech or args.prepositional_collocation or args.sentence) and (args.file or args.delimiter):
#     parser.error("Arguments '-d', '-pos', '-pc' and '-s' cannot be used along with '-f' or '-de' arguments.")


# validation of adding a new definition to a lexeme
# 2 approaches available:
#   a) adding a single definition via terminal (combination of -d, -pos, -pcol and -s arguments)
#   b) adding a batch of definitions via an external file (combination of -f and (optionally)-d arguments)

elif args.lexeme and args.append and ( ((args.definition or args.part_of_speech or args.prepositional_collocation or args.sentence) and (args.file or args.delimiter))  or
                                       (not args.definition and not args.part_of_speech and not args.file) ):
    parser.error("Incompatible use of -a command's arguments.")



if args.delimiter is None:
    args.delimiter = DEF_FILE_DELIMITER







if __name__ == '__main__':

    db_path =  DEF_DB_PATH if not args.database else args.database
    conn = sqlite3.connect(db_path)

    vocabulary = Vocabulary(conn=conn, name=os.path.basename(db_path))
    tester = Tester(vocabulary=vocabulary)


    def create_lexeme_definition(lexeme: Lexeme):
        try:
            vocabulary.create_lexical_entry(lexeme=lexeme)

            # vocabulary.create_LDPP(lexeme=Lexeme(lexeme=" ".join(args.lexeme), example_sentence=None),
                                
            #                         definition=WordDefinition(string=" ".join(args.definition), part_of_speech=PartOfSpeech[args.part_of_speech], sentence=" ".join(args.sentence) if args.sentence else None), 
            #                         lexeme_target=" ".join(args.lexeme_target) if args.lexeme_target else None)
        
            print("Operation successful!")
        
        except KeyError:
            print("Operation unsuccessful: Unknown value of -p parameter! Use -h for help.")
        except Exception as e:
            # print(e)
            print(f"Operation unsuccessful: {e}")

            # if isinstance(e, IllegalVocabularyState):
            #     pass
            # else:
            #     raise e

    if args.lexeme is not None:
 
        if args.append:
            # if args.definition and args.part_of_speech:
            # if not args.definition:
            #     print("Operation unsuccessful: Parameter '-d' required but not provided! Use -h for help.")
            # elif not args.part_of_speech:
            #     print("Operation unsuccessful: Parameter '-p' required but not provided! Use -h for help.")
            
            if args.file:
                # Open the CSV file
                # print("HHERE")
                with open(args.file, mode='r', encoding='utf-8') as src_file:
                    
                    # Create a CSV DictReader with the correct delimiter
                    reader = csv.DictReader(src_file, delimiter=args.delimiter)
                    
                    # Iterate over each row in the CSV
                    for row in reader:
                    
                        create_lexeme_definition(lexeme=Lexeme(lexeme=row['lexeme'], example_sentence=None,
                                                                definitions=[WordDefinition(string=row['definition'], lexeme_type=LexemeType[row['part_of_speech']],
                                                                                    collocate=row['collocate'] if row['collocate'] else None,
                                                                                    sentence=row['sentence'] if row['sentence'] else None)]))
            else:
                
                create_lexeme_definition(lexeme=Lexeme(lexeme=" ".join(args.lexeme), example_sentence=None,
                                                    definitions=[WordDefinition(string=" ".join(args.definition),
                                                                                lexeme_type=LexemeType[args.part_of_speech],
                                                                                collocate=" ".join(args.lexeme_target) if args.lexeme_target else None,
                                                                                sentence=" ".join(args.sentence) if args.sentence else None)]))
                # try:
                #     vocabulary.create_LDPP(lexeme=Lexeme(lexeme=" ".join(args.lexeme), example_sentence=None,
                #                                          definitions=[WordDefinition(string=" ".join(args.definition),
                #                                                                      part_of_speech=PartOfSpeech[args.part_of_speech],
                #                                                                      prepositional_collocation=" ".join(args.lexeme_target) if args.lexeme_target else None,
                #                                                                      sentence=" ".join(args.sentence) if args.sentence else None)]))

                #     # vocabulary.create_LDPP(lexeme=Lexeme(lexeme=" ".join(args.lexeme), example_sentence=None),
                                        
                #     #                         definition=WordDefinition(string=" ".join(args.definition), part_of_speech=PartOfSpeech[args.part_of_speech], sentence=" ".join(args.sentence) if args.sentence else None), 
                #     #                         lexeme_target=" ".join(args.lexeme_target) if args.lexeme_target else None)
                
                #     print("Operation successful!")
                
                # except KeyError:
                #     print("Operation unsuccessful: Unknown value of -p parameter! Use -h for help.")
                # except Exception as e:
                #     print(f"Operation unsuccessful: {e}")
                
        elif args.remove:

            try:
                vocabulary.delete_lexeme(string=" ".join(args.lexeme))
                print("Operation successful!")
            except Exception as e:
                print(f"Operation unsuccessful: {e}")
        
        elif args.all:
            vocabulary.print_all_definitions()

        # fetching a lexeme
        else:
            
            try:
                vocabulary.print_lexeme(word=" ".join(args.lexeme))
                print("Operation successful!")
            except Exception as e:
                raise e
                # print(f"Operation unsuccessful: {e}")
    
   
    elif args.definition:

        if args.remove:
            vocabulary.delete_definition(ID=int(args.definition[0]))


    elif args.vocabulary:

        if args.lexeme is None:
            vocabulary.print_vocabulary()
        elif not args.lexeme:
            vocabulary.print_all_lexemes()
    
    elif args.test:

        # if not tester.test_vocabulary(number_of_tests=args.test):
        #     print("No words in dictionary! At least 1 required for testing.\n")
        
        questions: List[TestQuestion] = tester.test_vocabulary(number_of_tests=args.test)

        if not questions:
            print("No words in dictionary! At least 1 required for testing.\n")
        
        else:
            print("Assign correct lexemes to the following definitions: ")

            for index, question in enumerate(questions):
                table = PrettyTable(field_names=['Expected Answer', 'Match Ratio', 'Sentence'])

                print(f"{index + 1}. {question.get_question()}: ", end="")

                question.answer(lexeme=input(""))
                # correct_answer, match_ratio, sentence = tester.submit_question(question=question)

                print("\nTEST RESULTS")
                table.add_row(tester.submit_question(question=question))
                print(table)
                print()
                # print(f"Expected answer: {correct_answer}, Match ratio: {match_ratio}")

        


        
        
        # # by doing this we prevent this scenario from happening later in the while loop
        # if not vocabulary.word_count():
        #     print("No words in dictionary! At least 1 required for testing.\n")
        # else:
        
        #     test_word_count = args.test
        #     tested_words = 0



        #     while test_word_count:

        #         # fetch all data with minimum test_count which were not tested (tested == 0)
        #         vocabulary.cursor.execute("""
        #             SELECT id, lexeme_id, definition_id, sentence
        #             FROM LDPP_instances
        #             WHERE tested = 0
        #             AND test_count = (
        #                 SELECT min(test_count) 
        #                 FROM LDPP_instances 
        #                 WHERE tested = 0
        #             );
        #         """)

        #         words = vocabulary.cursor.fetchall()

        #         random.shuffle(words)


        #         # this only means that all the words are tested (all with tested == 1)
        #         # a Test Round has been completed
        #         # here a transaction can be executed to keep database in consistent state
        #         if not words:
        #             vocabulary.cursor.execute("""
        #                 UPDATE LDPP_instances
        #                 SET tested = 0;
        #             """)

        #             vocabulary.conn.commit()

        #             continue



            
        #         for word in words:
        #             vocabulary.cursor.execute("SELECT test_count, passed_tests, sentence FROM LDPP_instances where id=(?)", (word[0],))
        #             update_attr = vocabulary.cursor.fetchone()



        #             vocabulary.cursor.execute("SELECT definition from definitions WHERE id = ?", (word[2], ))

        #             definition = vocabulary.cursor.fetchone()

        #             test_answer = input(f"{tested_words + 1}. {definition[0]}: ")

        #             vocabulary.cursor.execute("SELECT string from lexemes where id == ?;", (word[1], ))
        #             expected_answer = vocabulary.cursor.fetchone()[0]
        #             test_result = 1 if expected_answer == test_answer else 0

        #             print("CORRECT!", end=" ") if test_result else print(f"INCORRECT! Expected: {expected_answer}", end=" ")
        #             print(f"Sentence: {word[3]}")
        #             print(f"Success Rate: {(update_attr[1] + test_result) / (update_attr[0] + 1)}")

                    

        
        #             vocabulary.cursor.execute("""UPDATE LDPP_instances                      
        #                                         SET test_count=(?), tested=1, passed_tests= (?)
        #                                         WHERE id = (?); """, 
        #                                         # word_count is incremented, tested is set to 1, passed_tests are incremented only if test_asnwer == word.string
        #                                         (update_attr[0] + 1, update_attr[1] + test_result, word[0] ))
                    

        #             vocabulary.conn.commit()


        #             test_word_count -= 1
        #             tested_words += 1

        #             if test_word_count == 0:
        #                 break


    

    
    # vocabulary.disconnect()

        




    # vocabulary = None

    

    # ARG_DELIMITER = " "


    # def is_sentence(string: str):
    #     return string is not None and len(string) >= 2 and string[0].isupper() and string[-1] in ['.', '!', '?']


    # def print_help():
    #     print("""
    # Welcome to the CusVoc App! This script helps you manage your personal vocabulary. You can add new words manually, or use a public dictionary API for faster input.
    # CusVoc also provides test mechanisms to help you memorize the words more effectively.
            
    # COMMANDS:

    # -h, --help
    #     Display this help message.

    # -t, --terminate
    #     Exit the application.

    # -v, --vocabulary
    #     Load and display the number of words in the local vocabulary database.
        
    # -v <db_name>, --vocabulary <db_name>
    #     Load and display the vocabulary from the specified database.

    # -v -d, --vocabulary --disconnect
    #     Disconnect the currently connected vocabulary.

    # -v -all
    #     Display all words from the currently connected vocabulary.

    # -v -d -all, --vocabulary --definitions --all
    #     Display all definitions from the currently connected vocabulary.

    # -w <word>
    #     Fetch and display information about a specific word from the local vocabulary.
    #     Example: -w support

    # -w <word> -r, --word <word> --random
    #     Fetch and display information about a random word from the local vocabulary.

    # -w <word> -d, --word <word> --delete
    #     Delete a specific word from the local vocabulary.
    #     Example: -w support -d

    # -w <word> -a, --word <word> --append
    #     Add a new word and its definitions to the local vocabulary. Enter each definition as prompted, using the format:
    #     <definition> -p <part_of_speech> -s <sentence>
    #     Example: "Def 1: a thing that bears the weight of something or keeps it upright -p NOUN -s The pillar provides support."

    #     Type '---' when done entering definitions.

    #     If adding a sentence separately, use the -s flag after the definitions:
    #     Example: -w support -a -s

    # -t <number>, --test <number>
    #     Start a vocabulary test. Specify the number of words to test. Words are selected based on their test count and correctness in previous tests.
    #     Example: -t 10

    # IMPORTANT NOTES:
    #     - If <word> is actually a sequence of words, use _ instead of whitespace to separate them.
    #     - The test mechanism will reset after all words have been tested, allowing for continuous practice.
    # """)

   

    # while(True):
    #     command = input("Enter Command: ")

    #     comm_args = command.split(" ")
    #     comm_args_count = len(comm_args)

    #     # match comm_args[0]:
    #     if (comm_args[0] == "-v" or comm_args[0] == '--vocabulary') and comm_args_count == 1:
            
    #         if vocabulary is None:
    #             vocabulary = Vocabulary(db_name=DEF_DB_NAME)
            
    #         vocabulary.print_vocabulary()
    

    #     elif comm_args[0] == "-e" or comm_args[0] == '--exit':
    #         break

        
    #     elif comm_args[0] == "-h" or comm_args[0] == '--help':
    #         print_help()
        
    #     elif vocabulary is None and comm_args_count == 2 and (comm_args[0] == '-v' or comm_args[0] == '--vocabulary'):
            
           
     
    #         vocabulary = Vocabulary(db_name=comm_args[1])
    #         vocabulary.print_vocabulary()

                




        

    #     elif vocabulary is None:
    #         print("Vocabulary not loaded! See -h for help.\n")
    #         continue


    #     elif (comm_args[0] == '-v' or comm_args[0] == '--vocabulary'):
    #         if comm_args_count == 2: 
    #             if comm_args[1] == '-e' or comm_args[1] == '--exit':

    #                 if vocabulary is not None:
    #                     vocabulary.disconnect()
    #                     vocabulary = None
    #                     print("Vocabulary disconnected successfully!\n")
    #                 else:
    #                     print("No vocabulary connected! See -h for help.\n")
    #             elif comm_args[1] == '-all':
    #                 vocabulary.print_all_words()
    #             else:
    #                 print("A vocabulary already connected! See -h for help.\n")
    #         elif comm_args_count == 3:
    #             if comm_args[1] == '-d' or comm_args[1] == '--definitions' and comm_args[2] == '-all':
    #                 vocabulary.print_all_definitions()
    #         else:
    #             print("Invalid Command Format! See -h for help.\n")





    #     elif (comm_args[0] == '-t' or comm_args[0] == '--test') and comm_args_count == 2:
            


    #         # by doing this we prevent this scenario from happening later in the while loop
    #         if not vocabulary.word_count():
    #             print("No words in dictionary! At least 1 required for testing.\n")
    #             continue
            
    #         test_word_count = int(comm_args[1])
    #         tested_words = 0



    #         while test_word_count:

    #             # fetch all data with minimum test_count which were not tested (tested == 0)
    #             vocabulary.cursor.execute("""
    #                 SELECT id, word_id, definition_id
    #                 FROM vocabulary_definitions
    #                 WHERE tested = 0
    #                 AND test_count = (
    #                     SELECT min(test_count) 
    #                     FROM vocabulary_definitions 
    #                     WHERE tested = 0
    #                 );
    #             """)

    #             words = vocabulary.cursor.fetchall()

    #             random.shuffle(words)


    #             # this only means that all the words are tested (all with tested == 1)
    #             # a Test Round has been completed
    #             # here a transaction can be executed to keep database in consistent state
    #             if not words:
    #                 vocabulary.cursor.execute("""
    #                     UPDATE vocabulary_definitions
    #                     SET tested = 0;
    #                 """)

    #                 vocabulary.conn.commit()

    #                 continue



            
    #             for word in words:
    #                 vocabulary.cursor.execute("SELECT test_count, passed_tests, sentence FROM vocabulary_definitions where id=(?)", (word[0],))
    #                 update_attr = vocabulary.cursor.fetchone()



    #                 vocabulary.cursor.execute("SELECT definition, part_of_speech from definitions WHERE id = ?", (word[2], ))

    #                 definition = vocabulary.cursor.fetchone()

    #                 test_answer = input(f"{tested_words + 1}. {definition[0]}: ")

    #                 vocabulary.cursor.execute("SELECT string from vocabulary where id == ?;", (word[1], ))
    #                 expected_answer = vocabulary.cursor.fetchone()[0]
    #                 test_result = 1 if expected_answer == test_answer else 0

    #                 print("CORRECT!", end=" ") if test_result else print(f"INCORRECT! Expected: {expected_answer}", end=" ")
    #                 print(f"Sentence: {word[2]}")
    #                 print(f"Success Rate: {(update_attr[1] + test_result) / (update_attr[0] + 1)}")

                    

        
    #                 vocabulary.cursor.execute("""UPDATE vocabulary_definitions                      
    #                                           SET test_count=(?), tested=1, passed_tests= (?)
    #                                           WHERE id = (?); """, 
    #                                           # word_count is incremented, tested is set to 1, passed_tests are incremented only if test_asnwer == word.string
    #                                           (update_attr[0] + 1, update_attr[1] + test_result, word[0] ))
                    

    #                 vocabulary.conn.commit()


    #                 test_word_count -= 1
    #                 tested_words += 1

    #                 if test_word_count == 0:
    #                     break


                

    #     elif comm_args[0] == "-w" or comm_args[0] == '--word':
    #         if (comm_args_count == 2):

    #             if (comm_args[1] == '-r' or comm_args[1] == '--random'):
    #                 # vocabulary.prin
    #                 vocabulary.print_word(random.randint(a=0, b=vocabulary.word_count()))
                
    #             else:
    #                 vocabulary.print_word(word=comm_args[1])

    #         elif (comm_args_count == 3 or comm_args_count == 5 or comm_args_count == 7):
    #             if (comm_args[2] == '-d' or comm_args[2] == '--delete'):
    #                 vocabulary.delete_word(string=comm_args[1])
                
    #         # elif (comm_args_count == 3 or comm_args_count == 4):
    #             elif (comm_args[2] == '-a' or comm_args[2] == '--append') and comm_args_count > 4:
                    
    #                 # if vocabulary.contains_word(string=comm_args[1]):
    #                 #     print("A word with same string already inserted!\n")
    #                 #     continue


    #                 if (comm_args[3] == '-d' or comm_args[3] == '--definition') and (comm_args == 5 or comm_args[5] == '-t'):
                    
    #                     vocabulary.create_LDPP(lexeme=Lexeme(lexeme=comm_args[1].replace("_", " "), example_sentence=None, part_of_speech=PartOfSpeech.PREPOSITION),
    #                                            definition=WordDefinition(string=comm_args[4].replace("_", " ")))


    #                 # # def_count = int(comm_args[4])
    #                 # definitions: List[WordDefinition] = []
    #                 # command = input(f"Def {1}: ")
    #                 # def_i = 1

    #                 # # for definition in range(def_count):
    #                 # while command != '---':
                        
    #                 #     def_args = command.split(" -p ")

    #                 #     if len(def_args) != 2:
    #                 #         print("Invalid Definition Command Format! See -h for help.\n")
    #                 #         command = input(f"Def {def_i}: ")
    #                 #         continue
                        

    #                 #     def_i += 1

    #                 #     # processing PartOfSpeech and (potential) Sentence Argument, they are delimited by -s flag
    #                 #     def_args[1] = def_args[1].split(" -s ")

    #                 #     # after splitting def_args[1], it will always be an array
    #                 #     definitions.append(WordDefinition(string=def_args[0], part_of_speech=PartOfSpeech[def_args[1][0]], sentence=def_args[1][1] if len(def_args[1]) == 2 else None))

    #                 #     command = input(f"Def {def_i}: ")
                    
    #                 # if not definitions:
    #                 #     print("At least one definition required!")
    #                 #     continue
                    
    #                 # sentence = ""

    #                 # if comm_args_count == 4 and comm_args[3] == '-s':
    #                 #     command = input("Sentence: ")

                        
    #                 #     if is_sentence(string=command):
    #                 #         sentence = command
    #                 #     else:
    #                 #         print("Invalid Sentence Format or word not present! See -h for help.\n")
    #                 #         continue
                    
    #                 # vocabulary.create_LDPP(string=comm_args[1], definitions=definitions, sentence=sentence)    
                
                


    #                 # for i in range(test_word_count):
                        


    #             else:
    #                 print("Invalid Command Format! See -h for help.\n")


    print("Program terminated successfully!\n")

    if conn:
        tester.close()
        vocabulary.close()
        conn.close()
      