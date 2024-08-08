import requests
import sqlite3

import random
from typing import List

DEF_DB_NAME = 'vocabulary.db'



class Vocabulary():
    """
        Contains implementation of a database API for managing words in a vocabulary. 
        Tables in the database are based on a database schema and are built automatically when
        a new Vocabulary instance is created.
    """

    
    def __init__(self, db_name) -> None:
        

        self.name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                string TEXT NOT NULL UNIQUE,
                example_sentence TEXT,
                test_count INTEGER DEFAULT 0 NOT NULL
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS definitions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                definition TEXT NOT NULL UNIQUE
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary_definitions(
                word_id INTEGER NOT NULL,
                definition_id INTEGER NOT NULL,
                FOREIGN KEY(word_id) REFERENCES vocabulary(id),
                FOREIGN KEY(definition_id) REFERENCES definitions(id)
            );
        ''')


    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()


    def connect(self):
        self.conn = sqlite3.connect(self.name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()
    



    def create_word(self, string: str, definitions: List[str]):
        """
            A new word is inserted into database using a transaction. Provided string must be unique.
        """


        try:
            # Start transaction
            self.conn.execute('BEGIN')
            
            # Step 1: Insert the word into the Vocabulary table
            self.cursor.execute('SELECT id FROM vocabulary WHERE word = ?', (string,))
            word_row = self.cursor.fetchone()

            if word_row:
                print(f"Word '{string}' already exists in the database.\n")
                return  # Exit if the word is already in the database

            self.cursor.execute('''
                INSERT INTO vocabulary (word, test_count) 
                VALUES (?, 0)
            ''', (string,))
            vocabulary_id = self.cursor.lastrowid  # Get the id of the newly inserted word

            # Step 2: Insert definitions into the Definitions table
            definition_ids = []
            for definition_text in definitions:                    
                self.cursor.execute('SELECT id FROM definitions WHERE definition = ?', (definition_text,))
                definition_row = self.cursor.fetchone()
                
                if definition_row:
                    definition_id = definition_row[0]  # Get the existing definition id
                else:
                    self.cursor.execute('''
                        INSERT INTO definitions (definition) 
                        VALUES (?)
                    ''', (definition_text,))
                    definition_id = self.cursor.lastrowid  # Get the id of the newly inserted definition
                
                definition_ids.append(definition_id)

            # Step 3: Insert into VocabularyDefinitions table
            for definition_id in definition_ids:
                self.cursor.execute('''
                    INSERT INTO vocabulary_definitions (word_id, definition_id) 
                    VALUES (?, ?)
                ''', (vocabulary_id, definition_id))

            # Commit the transaction
            self.conn.commit()

        except Exception as e:
            # If an error occurs, rollback the transaction
            self.conn.rollback()
            print(f"An error occurred: {e}")
    



    def print_word(self, word: str | int):
        """
            This method pretty-prints a word and its attributes to the console.
        """


        word_attributes = self.get_word(string=word)

        if word_attributes is None:
            print("No word found!\n")
            return
        
        print(f"\nWORD: {word_attributes[1]}")
        print("---------------\n")

        print(f"SENTENCE: {word_attributes[2]}")
        print(f"TESTS: {word_attributes[3]}")


        self.cursor.execute("""
            SELECT definition_id from vocabulary_definitions
            WHERE word_id=(?)                
        """, (word_attributes[0], ))

        definition_ids = self.cursor.fetchall()

        print("MEANINGS")
        for index, id in enumerate(definition_ids):
            self.cursor.execute('''
                SELECT definition from definitions
                WHERE id == (?)
            ''', (int(id[0]), ))

            print(f"   {id[0]}. {self.cursor.fetchone()[0]}")

        print()





    def get_word(self, string: str | int):
        """
            Method retrieves a word from the table and returns it as a tuple.

            
            @params

            string - can either be a word or a sequence of words or integer representing the ordinal number of the searched word in the table
        """


        if isinstance(string, str):
            self.cursor.execute('SELECT * from vocabulary WHERE word == (?)', (string, ))
        elif isinstance(string, int):
            self.cursor.execute('''
                                   SELECT *  FROM vocabulary 
                                    LIMIT 1 
                                    OFFSET (?)-1;''', (string, ))

        return self.cursor.fetchone()
    


    def word_count(self):
        """
            Returns the total size of the Vocabulary table.
        """

        self.cursor.execute('SELECT COUNT(*) from vocabulary;')
        return int(self.cursor.fetchone()[0])





if __name__ == '__main__':
    vocabulary = None
    

    while(True):
        """
            Here command prompts received from user using console are processed.
        """


        command = input("Enter Command: ")
        comm_args = command.split(' ')

        if command == '-t' or command == '--terminate':
            break
        elif command == '-v' or command == '--vocabulary':
            
            # If reinitializing vocabulary the original is disconnected
            if vocabulary is not None:
                vocabulary.disconnect()

            # User can provide their custom database name, otherwise the default is used
            vocabulary = Vocabulary(db_name=DEF_DB_NAME if len(comm_args) == 1 else comm_args[1])
        
            print(f"Loaded local vocabulary with {vocabulary.word_count()} words!\n")
        elif command == '-h' or command == '--help':
            print("""
    Welcome to the CusVoc App! This script helps you manage your personal vocabulary. You can add new words
    manually but as a fast approach you can use public dictionary API.  CusVoc also provides test mechanisms to help you
    memorize the words more effectively.
            
            
    COMMANDS:

    -h, --help
        Display this help message.

    -t, --terminate
        Exit the application.

    -v, --vocabulary
        Load and display the number of words in the local vocabulary database.

    -w <word> -a, --word <word> --append
        Add a new word and its definitions to the local vocabulary. The word is fetched from a public dictionary API.
        Example: -w example_word -a

    -w <word>
        Fetch and display information about a specific word from the local vocabulary.
        Example: -w example_word

    -w <word> -p, --word <word> --public
        Fetch and display information about a specific word from the public dictionary API.
        Example: -w example_word -p
            
    IMPORTANT NOTES
        - If <word> is actually a sequence of words, use _ instead of whitespace to separate them.
            """)
        elif len(comm_args) == 3 and (comm_args[0] == '-w' or comm_args[0] == '--word') and (comm_args[2] == '-p' or comm_args[2] == '--public'):
 
            comm_args[1] = comm_args[1].replace('_', ' ')


            resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{comm_args[1]}')

            if resp.status_code == 200:
                word_instance = resp.json()[0] 

            
                print(f"WORD: {word_instance['word']}", end='\n\n')
                meanings = word_instance['meanings']
            
        
                print("MEANINGS")
                m_index = 1
                for meaning in meanings:
                    for definition in meaning['definitions']:
                        print(f"{m_index}. ({meaning['partOfSpeech']}) {definition['definition']}")
                        m_index += 1



        elif vocabulary is None:
            print("Vocabulary not loaded! Use -h for help.\n")




        # Possible commands for a loaded vocabulary


    
        else:



            if len(comm_args) == 2 and (comm_args[0] == '-w' or comm_args[0] == '--word') and (comm_args[1] == '-r' or comm_args[1] == '--random'):
                print(vocabulary.word_count())
                # print(vocabulary.get_word(0));
                print(vocabulary.get_word(random.randint(a=0, b=vocabulary.word_count())))




            elif len(comm_args) == 3 and (comm_args[0] == '-w' or comm_args[0] == '--word') and (comm_args[2] == '-a' or comm_args[2] == '--append'):

                comm_args[1] = comm_args[1].replace('_', ' ')
                resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{comm_args[1]}')


                if resp.status_code == 200:
                    definitions = []
                    meanings = resp.json()[0]['meanings']

                    for meaning in meanings:
                        for definition in meaning['definitions']:
                            definitions.append(definition['definition'])
                            # print(f"{m_index}. ({meaning['partOfSpeech']}) {definition['definition']}")
                            # m_index += 1

                    vocabulary.create_word(string=comm_args[1], definitions=definitions)
                
                print("New word added successfully.\n")




            elif len(comm_args) == 2 and (comm_args[0] == '-w' or comm_args[0] == '--word'):
                vocabulary.print_word(word=comm_args[1])
           
                
            
            else:
                
                print("Unknown command.")

    if vocabulary is not None:
        vocabulary.disconnect()

    print("Program terminated successfully!")