import sqlite3
from prettytable import PrettyTable
from dataclasses import dataclass

from language import LexemeType, Lexeme, COLLOCATES
# from code.src.voc_testing import get_match_ratio


def import_database_schema(conn: sqlite3.Connection):
    """
        Attempts to import a CusVoc Database Schema into database using provided sqlite3
        Connection Instance. This operation is executed atomically - if any part of the Importing
        Process fails, all changes made so far are automatically reversed.
    
        @params

            conn - instance of sqlite3 connection

        @prerequisites

            conn must be an active sqlite3 connection.
    """    



    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lexemes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                string TEXT NOT NULL UNIQUE,
                example_sentence TEXT
            );
        ''')
    

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS definitions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                definition TEXT NOT NULL UNIQUE
            );
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lexeme_types(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                type UNIQUE NOT NULL  
            )       
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collocates(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collocate TEXT NOT NULL UNIQUE
            )

        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LDPP_instances(
                id INTEGER PRIMARY KEY AUTOINCREMENT,      
                            
                lexeme_id INTEGER NOT NULL,
                definition_id INTEGER NOT NULL,
                part_of_speech_id INTEGER NOT NULL,
                collocate_id INTEGER,
                            
                sentence TEXT,

                test_count INTEGER DEFAULT 0 NOT NULL,
                total_match_ratio REAL DEFAULT 0 NOT NULL,
                tested INTEGER DEFAULT 0 NOT NULL,            
                


                FOREIGN KEY(lexeme_id) REFERENCES lexemes(id) ON DELETE CASCADE,
                FOREIGN KEY(definition_id) REFERENCES definitions(id) ON DELETE CASCADE,
                FOREIGN KEY(part_of_speech_id) REFERENCES lexeme_types(id) ON DELETE CASCADE,
                FOREIGN KEY(collocate_id) REFERENCES collocates(id) ON DELETE CASCADE
            );
        ''')

        
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e



def seed_lexeme_types(conn: sqlite3.Connection):
    """
        Attempts to seed all LexemeType values into database using provided sqlite3 Connection Instance. 
        If the table already contains the LexemeType value, it is skipped.

        This operation is executed atomically - if any part of the Importing
        Process fails, all changes made so far are automatically reversed.

        @params
            conn - instance of sqlite3 connection
        
        @prerequisites

            conn must be an active sqlite3 connection.

            table lexeme_types must be already present in the database.

            attribute type must be a column in lexeme_types table.

    """


    try:
        # seeding parts_of_speech table
        for POS in LexemeType:

            try:
                conn.cursor().execute("""
                    INSERT INTO lexeme_types(type)
                    VALUES (?)

                """, (POS.name.lower(),))

            # part-of-speech already inserted
            except sqlite3.IntegrityError:
                continue


            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e




def seed_collocates(conn: sqlite3.Connection):
    """
        Attempts to seed all Collocate values into database using provided sqlite3 Connection Instance. 
        If the table already contains the collocate, it is skipped.

        This operation is executed atomically - if any part of the Importing
        Process fails, all changes made so far are automatically reversed.

        @params
            conn - instance of sqlite3 connection
        
        @prerequisites

            conn must be an active sqlite3 connection.

            table collocates must be already present in the database

            attribute collocate must be a column in collocates table

    """


    # seeding lexeme targets

    try:
        for target in COLLOCATES:

            try:
                conn.cursor().execute("INSERT INTO collocates (collocate) VALUES (?)", (target, ))

            # target already inserted
            except sqlite3.IntegrityError:
                continue
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e





class IllegalVocabularyState(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)




class Vocabulary():
    """
        Vocabulary represents a public API available for users which provides all CRUD operations for an effective maintenance of a Personal Vocabulary.

        Data are stored locally via Sqlite Relational Database System. 
    """

    MAX_SENTENCE_CHAR_COUNT = 100
    
    def __init__(self, conn: sqlite3.Connection, name: str) -> None:
        """
            Initializes a new Vocabulary Instance dependent on the provided sqlite3 Connection Instance and with the provided name.

            A new Vocabulary Instance automatically reserves a new Cursor Instance from the Connection Instance.
            Predefined Database Schema for CusVoc Application is also automatically imported if not present.
            Tables lexeme_types and collocates are automatically seeded if not present.
        """
        
        self.conn = conn
        self.__cursor = self.conn.cursor()
        self.name = name

        
        import_database_schema(conn=self.conn)
        seed_lexeme_types(conn=self.conn)
        seed_collocates(conn=self.conn)

      





    def lexical_entries_size(self):
        """
            Returns a total count of Lexical Entries present in the current database.
        """

        self.__cursor.execute('SELECT COUNT(*) from lexemes;')
        return int(self.__cursor.fetchone()[0])
    

    def get_lexeme(self, ID: int):
        self.__cursor.execute('SELECT string from lexemes WHERE id = ?', (ID, ))
        lexeme = self.__cursor.fetchone()


        return lexeme[0] if lexeme else None
    
    
    def get_collocate(self, ID: int):
        self.__cursor.execute('SELECT collocate from collocates WHERE id = ?', (ID, ))
        pcol = self.__cursor.fetchone()

        return pcol[0] if pcol else None
    
    def get_definition(self, ID: int):
        self.__cursor.execute('SELECT definition from definitions WHERE id = ?', (ID, ))
        definition = self.__cursor.fetchone()


        return definition[0] if definition else None
    

    def get_lexeme_type(self, ID: int):
        self.__cursor.execute('SELECT type from lexeme_types WHERE id = ?', (ID, ))
        pos = self.__cursor.fetchone()


        return pos[0] if pos else None
    


    def print_vocabulary(self):
        print("\nVOCABULARY DETAILS")
        print("----------------------------\n")

        print(f'Name: \t\t"{self.name}"')
        print(f'Words: \t\t"{self.lexical_entries_size()}"')

        print()




    def create_lexical_entry(self, lexeme: Lexeme):

        try:
            if lexeme.definitions[0].sentence is not None and len(lexeme.definitions[0].sentence) > self.MAX_SENTENCE_CHAR_COUNT:
                raise IllegalVocabularyState(message="Provided sentence exceeds maximum limit of characters.")


    
            # if not lexeme:
            lexeme_id = None
            lexeme_already_present = False

            try:
                self.__cursor.execute("""
                    INSERT INTO lexemes (string, example_sentence)
                    VALUES (?, ?)

                """, (lexeme.lexeme, lexeme.example_sentence))
                lexeme_id = self.__cursor.lastrowid
            
            except sqlite3.IntegrityError:
                lexeme_already_present = True
        

                self.__cursor.execute("""
                    SELECT id from lexemes WHERE string == ?

                """, (lexeme.lexeme, ))

                lexeme_id = self.__cursor.fetchone()

                assert(lexeme_id)
                
                lexeme_id = lexeme_id[0]
                # lexeme is already in database, a new definition can still be inserted though

            collocate_id = None

            if lexeme.definitions[0].collocate is not None:
                self.__cursor.execute("""
                    SELECT id FROM collocates WHERE collocate = ?
                """, (lexeme.definitions[0].collocate, ))

                collocate_id = self.__cursor.fetchone()

                if collocate_id is None:
                    self.__cursor.execute("""
                        INSERT INTO collocates (collocate) VALUES (?)
                    """, (lexeme.definitions[0].collocate, ))

                    self.conn.commit()

                    collocate_id = self.__cursor.lastrowid
                else:
                    collocate_id = collocate_id[0]

            


            
            # searching for a preposition match in database
            # prep_id = None
            # if lexeme.definitions[0].prepositional_collocation is not None:

            #     self.cursor.execute("""
            #         SELECT id FROM preposition_collocations
            #         WHERE pcol = (?)       
            #     """, (lexeme.definitions[0].prepositional_collocation, ))

            #     prep_id = self.cursor.fetchone()


            #     # search preposition was not found in database - illegal vocabulary state
            #     if not prep_id:
            #         raise IllegalVocabularyState(message="Unknown preposition!")
                
            #     prep_id = prep_id[0]


            # fetching either an already existent definition (with the same definition string) from database or creating a new one
            
            definition_id = None
            definition_already_present = True

            self.__cursor.execute("""
                SELECT id from definitions where definition == ?
            """, (lexeme.definitions[0].string, ))   

            definition_id = self.__cursor.fetchone()

            # if a definition has not already been added to database new one is inserted
            if not definition_id:
                definition_already_present = False
                self.__cursor.execute("INSERT INTO definitions (definition) VALUES (?)", (lexeme.definitions[0].string, ))
                definition_id =  self.__cursor.lastrowid
            else:
                definition_id = definition_id[0]


            
            if lexeme_already_present and definition_already_present:
                raise IllegalVocabularyState(message="A lexeme with the same definition already present in database!")
            

            self.__cursor.execute("""
                INSERT INTO LDPP_instances (lexeme_id, definition_id, part_of_speech_id, collocate_id, sentence)
                VALUES (?, ?, ?, ?, ?)
                
            """, (lexeme_id, definition_id, lexeme.definitions[0].lexeme_type.value, collocate_id, lexeme.definitions[0].sentence))
        
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            raise e
            



    def print_lexeme(self, word: str | int):
        """
            This method pretty-prints a word and its attributes to the console.
        """


        lexeme_attributes = self.get_word(string=word)

        if lexeme_attributes is None:
            print("Word not found!\n")
            return
        



        self.__cursor.execute("""
            SELECT definition_id, test_count, part_of_speech_id, sentence, total_match_ratio from LDPP_instances
            WHERE lexeme_id=(?)                
        """, (lexeme_attributes[0], ))

        LDPP_attributes = self.__cursor.fetchall()

        # print(f'Tests_in_total: \t"{lexeme_attributes[3]}"')

        table = PrettyTable()
        table.field_names = ['No.', 'ID', 'Meaning', 'Part-of-Speech', 'Sentence', 'Tests', 'Total Match Rate']

        print(f"\nFollowing data found for lexeme '{lexeme_attributes[1]}'")
        # print(f"\nMeanings \t PartOfSpeech \t\t Definition \t \t Tests")
        
        for index, attribute in enumerate(LDPP_attributes):
            
            self.__cursor.execute('''
                SELECT id, definition from definitions
                WHERE id == (?)
            ''', (int(attribute[0]), ))

            definition_row = self.__cursor.fetchone()
            part_of_speech = None

            for part in LexemeType:
                if part.value == int(attribute[2]):
                    part_of_speech = part.name
                    break
            else:
                raise IllegalVocabularyState(message="The LDPP instance has invalid part-of-speech-id assigned!")
            
            table.add_row([index + 1, definition_row[0], definition_row[1], part_of_speech, attribute[3], attribute[1], attribute[4] / attribute[1] if attribute[1] > 0 else '---'])

        print(table)

        print()



    def print_all_lexemes(self):
        self.__cursor.execute("""
            SELECT id, string from lexemes;
        """)

        lexeme_attributes = self.__cursor.fetchall()

        if not lexeme_attributes:
            print("Vocabulary is empty.")
            return

        

        table = PrettyTable()
        table.field_names = ['No.', 'Lexeme', 'Total Tests']

        print()

        print("VOCABULARY")
        # print("-----------------------")
        
        # print()

        for index, attribute in enumerate(lexeme_attributes):
            self.__cursor.execute("""
                SELECT SUM(test_count) FROM LDPP_instances WHERE lexeme_id = ?
            """, (attribute[0], ) )

            total_tests = self.__cursor.fetchone()[0]
            table.add_row([index + 1, attribute[1], total_tests])


        print(table)



    def print_all_definitions(self):
        self.__cursor.execute("""
            SELECT lexeme_id, definition_id, test_count, tested, total_match_ratio from LDPP_instances;
        """)

        vocabulary_definitions = self.__cursor.fetchall()

        try:
            print("\nDEFINITIONS")

            table = PrettyTable()
            table.field_names = ['No.', 'Lexeme', 'Meaning', 'Total Tests', 'Passed Tests', 'Match Rate']

            for index, voc_def in enumerate(vocabulary_definitions):

                self.__cursor.execute("SELECT string from lexemes WHERE id == ?", (voc_def[0], ))
                string = self.__cursor.fetchone()[0]

                self.__cursor.execute("SELECT definition from definitions WHERE id == ?", (voc_def[1], ))
                definition = self.__cursor.fetchone()[0]
                

                table.add_row([index + 1, string, definition, voc_def[2], voc_def[4], voc_def[4] / voc_def[2] if voc_def[2] > 0 else 0])                 
                
            print(table)
            print()

        except Exception as e:
            raise e



    def contains_lexeme(self, lexeme: str):

        self.__cursor.execute("SELECT id from lexemes where string = (?)", (lexeme, ))
        return True if self.__cursor.fetchone() else False
        



    def get_word(self, string: str | int):
        """
            Method retrieves a word from the table and returns it as a tuple.

            
            @params

            string - can either be a word or a sequence of words or integer representing the ordinal number of the searched word in the table
        """


        if isinstance(string, str):
            self.__cursor.execute('SELECT * from lexemes WHERE string == (?)', (string, ))
        elif isinstance(string, int):
            self.__cursor.execute('''
                                   SELECT *  FROM lexemes 
                                    LIMIT 1 
                                    OFFSET (?)-1;''', (string, ))

        return self.__cursor.fetchone()
    



    def delete_lexeme(self, string: str):
        self.__cursor.execute('DELETE FROM lexemes WHERE string == (?)', (string, ))

        # user cannot remove multiple words
        assert(self.__cursor.rowcount <= 1)

        print("Lexeme removed successfully!\n") if self.__cursor.rowcount == 1 else print("Lexeme not found!\n")


        self.conn.commit()

    
    def delete_definition(self, ID: int):
        self.__cursor.execute('DELETE FROM definitions WHERE id = ?', (ID, ))

        # user cannot remove multiple definitions
        assert(self.__cursor.rowcount <= 1)

        print("Definition removed successfully!\n") if self.__cursor.rowcount == 1 else print("Definition not found!\n")

        self.conn.commit()
    

    def close(self):
        self.__cursor.close()
    