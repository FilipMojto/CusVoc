import Levenshtein
from dataclasses import dataclass
import sqlite3
from typing import List, Dict
import random

from vocabulary import Vocabulary
from language import WordDefinition


def get_match_ratio(user_input, correct_lexeme, threshold=0.8):
    # Compute similarity ratio
    similarity = Levenshtein.ratio(user_input, correct_lexeme)

    # Check if similarity is above the threshold
    return similarity, similarity >= threshold



class IllegalTesterState(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)




@dataclass
class LexicalEntry(WordDefinition):

    id: int = None
    test_count: int = 0
    was_tested: bool = False
    total_match_ratio: float = 0
    for_practice: bool = False



class TestQuestion():

    def __init__(self, instance: LexicalEntry) -> None:
        self.__instance = instance
        # self.__lexeme = lexeme
        self.__answer = None
        
    
    def get_instance_id(self):
        return self.__instance.id


    def answer(self, lexeme: str):
        self.__answer = lexeme

    def get_submitted_answer(self):
        return self.__answer
    
    def get_question(self):
        return self.__instance.string
    







class Tester():

    ############# CONSTRUCTOR #############

    def __init__(self, vocabulary: Vocabulary) -> None:
        # Vocabulary.__init__(self, conn=conn)

        self.vocabulary = vocabulary
        self.conn = self.vocabulary.conn
        self.__cursor = self.conn.cursor()

                                                    # expected lexeme, sentence
        self.__pending_questions: Dict[TestQuestion, tuple[str, str]] = {}

        self.__check_tested_flag()



    ############## PUBLIC API ##############


    def clear_questions(self):
        self.__pending_questions.clear()


    def submit_questions(self):
        
        
        # try:
            for question  in self.__pending_questions.keys():
                
                self.submit_question(question=question)


            
    def submit_question(self, question: TestQuestion):

        assert(question in self.__pending_questions)


         
        

        correct_answer, sentence = self.__pending_questions[question]
        match_ratio, accepted = get_match_ratio(user_input=question.get_submitted_answer(), correct_lexeme=correct_answer)

        self.__cursor.execute("""
            UPDATE LDPP_instances
            SET test_count = test_count + 1,
                tested = 1,
                total_match_ratio = total_match_ratio + ?
            WHERE id = ?
            """, (match_ratio, question.get_instance_id()))

        self.conn.commit()

        self.__pending_questions.pop(question)

        self.__check_tested_flag()

        
        return correct_answer, match_ratio, sentence

    def test_vocabulary(self, number_of_tests: int):

        if self.__pending_questions:
            raise IllegalTesterState(message="Cannot provide more questions while there are questions pending!")

        # by doing this we prevent this scenario from happening later in the while loop
        if not self.vocabulary.lexical_entries_size():
            # print("No words in dictionary! At least 1 required for testing.\n")
            return []

        # fetch all data which were not tested (tested == 0)
        self.__cursor.execute("""
            SELECT id, lexeme_id, definition_id, part_of_speech_id, collocate_id, sentence, test_count, tested, total_match_ratio
            FROM LDPP_instances
            WHERE tested = 0"""
        );
                             

       
        questions = self.__extract_questions(LDPP_instances=self.__cursor.fetchall(), question_no=number_of_tests)
        number_of_tests -= len(questions)

            

        while number_of_tests:
            self.__cursor.execute("""
                SELECT id, lexeme_id, definition_id, part_of_speech_id, collocate_id, sentence, test_count, tested, total_match_ratio
                FROM LDPP_instances"""
            );
        

            new_questions = self.__extract_questions(LDPP_instances=self.__cursor.fetchall(), question_no=number_of_tests)

            number_of_tests -= len(new_questions)
            questions.extend(new_questions)


        return questions
    
    def close(self):
        self.__cursor.close()
            


    ############## PRIVATE API ################

    def __check_tested_flag(self):
        # Check if all rows are set to tested = 1
        self.__cursor.execute("SELECT COUNT(*) FROM LDPP_instances WHERE tested = 1")
        count_tested = self.__cursor.fetchone()[0]

        self.__cursor.execute("SELECT COUNT(*) FROM LDPP_instances")
        total_rows = self.__cursor.fetchone()[0]

        # If all rows are tested
        if count_tested == total_rows and total_rows > 0:
            # Reset all rows to tested = 0
            self.__cursor.execute("UPDATE LDPP_instances SET tested = 0")
            self.conn.commit()        

    

    def __extract_questions(self, LDPP_instances, question_no: int):
        random.shuffle(LDPP_instances)

        questions: List[TestQuestion] = []

        for instance in LDPP_instances:

           
            question = TestQuestion(LexicalEntry(string=self.vocabulary.get_definition(ID=int(instance[2])),
                                                  lexeme_type=self.vocabulary.get_lexeme_type(ID=int(instance[3])),
                                                collocate=self.vocabulary.get_collocate(ID=int(instance[4])) if instance[4] else None,
                                                sentence=instance[5],
                                                id=instance[0],
                                                test_count=int(instance[6]),
                                                was_tested=bool(instance[7]),
                                                total_match_ratio=float(instance[8])))
            

            self.__pending_questions[question] = (self.vocabulary.get_lexeme(ID=int(instance[1])), instance[5])

            questions.append(question)

            question_no -= 1

            if not question_no:
                return questions
        
        return questions


    