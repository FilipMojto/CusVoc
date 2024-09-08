import Levenshtein
from typing import List, Dict, Literal
import random
from peewee import _transaction
from datetime import datetime

from vocabulary import Vocabulary, ContraintViolationError

from models.lexical_entry import LexicalEntry
# from models.lexeme import Lexeme


def get_match_ratio(user_input, correct_lexeme, threshold=0.8):
    # Compute similarity ratio
    similarity = Levenshtein.ratio(user_input, correct_lexeme)

    # Check if similarity is above the threshold
    return similarity, similarity >= threshold



class IllegalTesterState(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class QuestionNotFound(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

# @dataclass
# class LexicalEntry(WordDefinition):

#     id: int = None
#     test_count: int = 0
#     was_tested: bool = False
#     total_match_ratio: float = 0
#     for_practice: bool = False



class TestQuestion():

    def __init__(self, meaning: str, lexeme: str, mode: Literal['normal', 'for_practice'] = 'normal') -> None:
        self.__meaning = meaning
        # self.__lexeme = lexeme
        self.__answer = None
        self.__lexeme = lexeme
        self.__is_submitted = False
        self.__evaluation: float = None
        self.__mode = mode

        
    
    # def get_instance_id(self):
    #     return self.__meaning.get_id()



    def answer(self, lexeme: str):
        self.__answer = lexeme

    def submit(self):
        self.__is_submitted = True

    def is_submitted(self):
        return self.__is_submitted

    def get_answer(self):

        if not self.__is_submitted:
            return None
        
        return self.__answer
    
    def ask(self):
        return self.__meaning

    def get_question(self):
        return self.__lexeme
    
    
    def evaluate(self, match_ratio: float):
        if not self.__is_submitted:
            return False

        self.__evaluation = match_ratio
        return True
    
    def get_evaluation(self):
        return self.__evaluation
    
    def get_mode(self):
        return self.__mode

    







class Tester():
    MAX_QUESTION_BUFFER_SIZE = 1000

    ############# CONSTRUCTOR #############

    def __init__(self, vocabulary: Vocabulary) -> None:
        # Vocabulary.__init__(self, conn=conn)

        self.vocabulary = vocabulary
        # self.conn = self.vocabulary.get_connection()
        # self.__cursor = self.conn.cursor()

                                                    # expected lexeme, sentence
        # self.__pending_questions: Dict[TestQuestion, tuple[str, str]] = {}
        self.__question_buffer: Dict[TestQuestion, tuple[LexicalEntry, Literal['clear', 'set']]] = {}

        self.__clear_was_tested_flag()



    ############## PUBLIC API ##############


    def clear_questions(self):
        self.__question_buffer.clear()


    def submit_questions(self):
        
        
        # try:
            for question  in self.__question_buffer.keys():
                
                self.submit_question(question=question)


            
    def submit_question(self, question: TestQuestion):

        if not question in self.__question_buffer:
            raise QuestionNotFound(message="Provided question not found in question buffer!")
        
        question.submit()
        # question.

         
        

        entry, op = self.__question_buffer[question]
    
        match_ratio, accepted = get_match_ratio(user_input=question.get_answer(), correct_lexeme=entry.lexeme.string)

        with _transaction(db=self.vocabulary.database()):
            # entry: LexicalEntry = LexicalEntry.get_by_id(question.get_instance_id())
            # entry = self.__question_buffer[question]
        
            entry.test_count += 1

            if question.get_mode() == 'normal':
                entry.was_tested = True 
            else:
                entry.was_practiced = True


            entry.match_sum += match_ratio
            entry.tested_at = datetime.now()

            entry.save()


        # self.__cursor.execute("""
        #     UPDATE lexical_entries
        #     SET test_count = test_count + 1,
        #         tested = 1,
        #         total_match_ratio = total_match_ratio + ?
        #     WHERE id = ?
        #     """, (match_ratio, question.get_instance_id()))

        # self.conn.commit()

        self.__question_buffer.pop(question)

        self.__clear_was_tested_flag()

        question.evaluate(match_ratio=round(match_ratio * 100, 2))
        return entry
    
        # return correct_answer, match_ratio, sentence




    # def test_vocabulary(self, number_of_tests: int):
    #     if number_of_tests > self.MAX_QUESTION_BUFFER_SIZE:
    #         raise IllegalTesterState(message=f"Number of tests exceeds maximum limit ({self.MAX_QUESTION_BUFFER_SIZE})!")

    #     if self.__question_buffer:
    #         raise IllegalTesterState(message="Cannot provide more questions while there are questions pending!")

    #     # by doing this we prevent this scenario from happening later in the while loop
    #     if not self.vocabulary.lexical_entry_count():
    #         # print("No words in dictionary! At least 1 required for testing.\n")
    #         return None
        

    #     while number_of_tests:


    #     # fetch all data which were not tested (tested == 0)

    #         # untested_entries = LexicalEntry.select().where(LexicalEntry.was_tested == False)
    #         new_questions: List[TestQuestion] = []
    #         untested_entries = list(LexicalEntry.select().where(LexicalEntry.was_tested == False))

    #         if untested_entries:
    #             new_questions.extend(self.__extract_questions(lexical_entries=untested_entries, question_no=number_of_tests))
    #         else:
    #             new_questions.extend(self.__extract_questions(lexical_entries=list(LexicalEntry.select()), question_no=number_of_tests))

    #     # self.__cursor.execute("""
    #     #     SELECT id, lexeme_id, definition_id, part_of_speech_id, collocate_id, sentence, test_count, tested, total_match_ratio
    #     #     FROM lexical_entries
    #     #     WHERE tested = 0"""
    #     # );
                             

       
    #         # self.__extract_questions(lexical_entries=untested_entries, question_no=number_of_tests)
    #         number_of_tests -= len(new_questions)
    #         # else:


            

    #     # while number_of_tests:
    #     #     # l_entries = LexicalEntry.select()

    #     #     # l_entries 
    #     #     # self.__cursor.execute("""
    #     #     #     SELECT id, lexeme_id, definition_id, part_of_speech_id, collocate_id, sentence, test_count, tested, total_match_ratio
    #     #     #     FROM lexical_entries"""
    #     #     # );
        

    #     #     new_questions = self.__extract_questions(lexical_entries=LexicalEntry.select(), question_no=number_of_tests)

    #     #     number_of_tests -= len(new_questions)
    #     #     questions.extend(new_questions)


    #     return new_questions
    
    # def close(self):
    #     self.__cursor.close()
    
    # def __weighted_choice(self, entries, weights):
    #     return random.choices(entries, weights=weights, k=1)[0]
    
    def __create_question(self, entry: LexicalEntry, undo_op: Literal['clear', 'set']):
        question = TestQuestion(meaning=entry.definition.definition, lexeme=entry.lexeme.string)
        self.__question_buffer[question] = (entry, undo_op)
        return question


    def __get_questions(self, count: int, field_name: Literal['was_tested', 'was_practiced']):
        field = getattr(LexicalEntry, field_name)
        print(field)
        print(f"Entries: {len(LexicalEntry.select())}")
        candidate_entries = LexicalEntry.select().where(LexicalEntry.for_practice == True) if field_name == 'was_practiced' else LexicalEntry.select()

        questions: List[TestQuestion] = []
        
        print(count)
        print(f"Entries: {len(candidate_entries)}")

        if len(candidate_entries) < count:
            raise ContraintViolationError(message="Required test amount exceeds the number of entries for practice in database.")
        # print(count)
        undo_op: Literal['clear', 'set'] = 'clear'
        
        while count:
            # for_practice_entries.wher
            untested_candidates = list(candidate_entries.where(field == False))
            
            for entry in untested_candidates:
                if field == 'was_practiced':
                    entry.was_practiced = True
                else:
                    entry.was_tested = True
            
            LexicalEntry.bulk_update(untested_candidates, fields=[field])


            # candidates.extend(untested_for_practice_entries)

            # if len(entries) < expected_entry_count:
            #     raise ContraintViolationError(message="Required test amount exceeds the number of entries for practice in database.")

            random.shuffle(untested_candidates)

            actual_entry_count = min(count, len(untested_candidates))
            
            # number_of_tests -= actual_entry_count
            count -= actual_entry_count

            for i in range(actual_entry_count):
                
                questions.append(self.__create_question(entry=untested_candidates[i], undo_op=undo_op))
            
            # all for-practice entries have been tested, reset was_practiced flags
            if count:
                # entries = LexicalEntry.select().where(for_practice == True)
                LexicalEntry.update({field:False}).where(field == True)
                undo_op = 'set'

                # for entry in entries:
                #     entry.was_practiced = False
        
                # LexicalEntry.bulk_update(entries)
            
        # print(questions)    
        return questions

        # number_of_tests -= expected_entry_count

        # entries.clear()



    def test_vocabulary(self, number_of_tests: int, for_practice: int = 0, practice_mode: Literal['number', 'percentage'] = 'number'):

        

        if self.__question_buffer:
            raise IllegalTesterState(message="Cannot provide more questions while there are questions pending!")
        
        
        if number_of_tests > self.MAX_QUESTION_BUFFER_SIZE:
            raise IllegalTesterState(message=f"Number of tests exceeds maximum limit ({self.MAX_QUESTION_BUFFER_SIZE})!")
        
        with self.vocabulary.database().atomic() as transaction:
            try:
                total_entry_count = self.vocabulary.lexical_entry_count()

                
                if not total_entry_count:
                    return None

                print(total_entry_count)
                if number_of_tests > total_entry_count:
                    raise IllegalTesterState(message=f"Number of tests exceeds the total number of entries in database ({total_entry_count})")

                new_questions: List[TestQuestion] = []
                # entries: List[LexicalEntry] = []

                if for_practice:
                    new_questions.extend(self.__get_questions(count=int((number_of_tests / 100) * for_practice) if practice_mode == 'percentage' else for_practice, field_name='was_practiced'))
                    number_of_tests -= len(new_questions)

                new_questions.extend(self.__get_questions(count=number_of_tests, field_name='was_tested'))
                    # expected_entry_count = int((number_of_tests / 100) * for_practice) if practice_mode == 'percentage' else for_practice



                #     for_practice_entries = LexicalEntry.select().where(LexicalEntry.for_practice == True)

                #     if len(for_practice_entries) < expected_entry_count:
                #         raise ContraintViolationError(message="Required test amount exceeds the number of entries for practice in database.")

                #     undo_op: Literal['clear', 'set'] = 'clear'

                #     while expected_entry_count:
                #         # for_practice_entries.wher
                #         untested_for_practice_entries = for_practice_entries.where(LexicalEntry.was_practiced == False)

                #         for entry in untested_for_practice_entries:
                #             entry.was_practiced = True
                        
                #         LexicalEntry.bulk_update(untested_for_practice_entries)


                #         entries.extend(untested_for_practice_entries)

                #         # if len(entries) < expected_entry_count:
                #         #     raise ContraintViolationError(message="Required test amount exceeds the number of entries for practice in database.")

                #         random.shuffle(entries)

                #         actual_entry_count = min(expected_entry_count, len(entries))
                #         number_of_tests -= actual_entry_count
                #         expected_entry_count -= actual_entry_count

                #         for i in range(actual_entry_count):
                #             new_questions.append(self.__create_question(entry=entries[i], undo_op=undo_op))
                        
                #         # all for-practice entries have been tested, reset was_practiced flags
                #         if expected_entry_count:
                #             # entries = LexicalEntry.select().where(for_practice == True)
                #             LexicalEntry.update({LexicalEntry.was_practiced:False}).where(for_practice == True)
                #             undo_op = 'set'

                #             # for entry in entries:
                #             #     entry.was_practiced = False
                    
                #             # LexicalEntry.bulk_update(entries)
                        
                        


                #     # number_of_tests -= expected_entry_count

                #     entries.clear()
            except Exception as e:
                transaction.rollback()
                raise e

                # random.shuffle(for_practice_entries)

                



            
            # while True:
            #     entries.extend(LexicalEntry.select().where(LexicalEntry.was_tested == False))
            #     random.shuffle(entries)
            #     # Assign higher weights to `for_practice` entries
            #     # weights = [3 if entry.for_practice else 1 for entry in entries]
                
            #     for entry in entries:
            #         # selected_entry = self.__weighted_choice(entries, weights)
            #         # question = TestQuestion(meaning=entries[i].definition.definition, lexeme=entries[i].lexeme.string)
            #         # self.__question_buffer[question] = entries[i]
            #         # print(i)
            #         new_questions.append(self.__create_question(entry=entry))

            #         number_of_tests -= 1

            #         if not number_of_tests:
            #             break
                
                
                
            #     if not number_of_tests:
            #         break

                    # number_of_tests -= 1

            return new_questions


    ############## PRIVATE API ################

    def __clear_was_tested_flag(self):

        entry_count = LexicalEntry.select().where(LexicalEntry.was_tested == True).count()

        # self.vocabulary.lexical_entry_count()

        if entry_count == self.vocabulary.lexical_entry_count():
            with _transaction(db=self.vocabulary.database()):

                LexicalEntry.update(was_tested=False).execute()

        entry_count = LexicalEntry.select().where(LexicalEntry.was_practiced == True).count()

        # self.vocabulary.lexical_entry_count()

        if entry_count == LexicalEntry.select().where(LexicalEntry.for_practice == True).count():
            with _transaction(db=self.vocabulary.database()):

                LexicalEntry.update(was_practiced=False).execute()





        # # Check if all rows are set to tested = 1
        # self.__cursor.execute("SELECT COUNT(*) FROM lexical_entries WHERE was_tested = 1")
        # count_tested = self.__cursor.fetchone()[0]

        # self.__cursor.execute("SELECT COUNT(*) FROM lexical_entries")
        # total_rows = self.__cursor.fetchone()[0]

        # # If all rows are tested
        # if count_tested == total_rows and total_rows > 0:
        #     # Reset all rows to tested = 0
        #     self.__cursor.execute("UPDATE lexical_entries SET was_tested = 0")
        #     self.conn.commit()        

    

    def __extract_questions(self, lexical_entries: List[LexicalEntry], question_no: int):
        random.shuffle(lexical_entries)

    

        questions: List[TestQuestion] = []

        for entry in lexical_entries:
            question = TestQuestion(meaning=entry.definition.definition, lexeme=entry.lexeme.string)
            
            # question = TestQuestion(LexicalEntry(string=self.vocabulary.get_definition(ID=int(instance[2])),
            #                                       lexical_category=self.vocabulary.get_lexical_category(ID=int(instance[3])),
            #                                     collocate=self.vocabulary.get_collocate(ID=int(instance[4])) if instance[4] else None,
            #                                     sentence=instance[5],
            #                                     id=instance[0],
            #                                     test_count=int(instance[6]),
            #                                     was_tested=bool(instance[7]),
            #                                     total_match_ratio=float(instance[8])))
            
            self.__question_buffer[question] = entry
            # self.__question_buffer.append(question)
            # self.__pending_questions[question] = (self.vocabulary.get_lexeme(ID=int(instance[1])), instance[5])

            questions.append(question)

            question_no -= 1

            if not question_no:
                return questions
        
        return questions


    