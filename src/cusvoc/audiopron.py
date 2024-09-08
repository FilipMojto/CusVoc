
from requests import get
from urllib.error import HTTPError
import tempfile
import os, sys

# here we hide the messages printed by pygame when importing
sys.stdout = open(os.devnull, 'w')
from pygame import mixer, time
sys.stdout = sys.__stdout__ 


from vocabulary import Vocabulary, LexemeNotFoundError, Lexeme


PUBLIC_DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


def play_audio_file(path: str):
    try:
        mixer.init()
        mixer.music.load(path)
        
        mixer.music.play()
        
        while mixer.music.get_busy():
            time.Clock().tick(10)  # Add a short delay to prevent high CPU usage
    finally:
        mixer.music.stop()
        mixer.quit()



def play_temp_audio_file(content):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
        temp_audio_file.write(content)
        temp_audio_file.flush()

        # Save the path to the file
        temp_audio_file_path = temp_audio_file.name

    try:
        mixer.init()
        # Load and play the audio file using pygame
        mixer.music.load(temp_audio_file_path)
        mixer.music.play()

        # Keep the script running until the audio finishes playing
        while mixer.music.get_busy():
            time.Clock().tick(10)
    finally:
        mixer.music.stop()
        mixer.quit()
        # Clean up the temporary file
        os.remove(temp_audio_file_path)




def extract_audio_content_from_api(lexeme: str):
    lexeme_response = get(url=PUBLIC_DICTIONARY_API_URL + lexeme)

    if lexeme_response.status_code == 200:
        lexeme_response = lexeme_response.json()
        lexeme_response = lexeme_response[0]

        pronunciation_audio_url = lexeme_response['phonetics'][1]['audio']
        pronunciation_audio_response = get(pronunciation_audio_url)

        
        if pronunciation_audio_response.status_code != 200:
            raise HTTPError(url=PUBLIC_DICTIONARY_API_URL + lexeme, code=lexeme_response.status_code)
        
        return pronunciation_audio_response.content

    else:
        raise HTTPError(url=PUBLIC_DICTIONARY_API_URL + lexeme, code=lexeme_response.status_code)
    



class PhoneticsAudioManager():

    def __init__(self, vocabulary: Vocabulary, PAC_dir: str):
        self.vocabulary = vocabulary
        self.__PAC_dir = PAC_dir



    def create_PAC(self, lexeme_identifier: int | str):
        lexeme: Lexeme = None

        
        if isinstance(lexeme_identifier, int):
            lexeme = Lexeme.select().where(Lexeme.id == lexeme_identifier).get()
        elif isinstance(lexeme_identifier, str):
            lexeme = Lexeme.select().where(Lexeme.string == lexeme_identifier).get()
        
        

        if lexeme is None:
            raise LexemeNotFoundError(f"Lexeme with ID or name '{lexeme_identifier}' not found.")
        
        if lexeme.PAC_file_path:
            return False

   

        audio_content = extract_audio_content_from_api(lexeme=lexeme.string)
        file_path = self.__PAC_dir + lexeme.string + '.mp3'
        open(file=file_path, mode='x')

        with open(file=file_path, mode='wb') as audio_file:
            audio_file.write(audio_content)

        lexeme.PAC_file_path = file_path

        lexeme.save()

        
        return True
    

    def delete_PAC(self, lexeme_identifier: int | str):
        
        if isinstance(lexeme_identifier, int):
            lexeme: Lexeme = Lexeme.get(Lexeme.id == lexeme_identifier)
        elif isinstance(lexeme_identifier, str):
            lexeme: Lexeme = Lexeme.get(Lexeme.string == lexeme_identifier)


        if lexeme.PAC_file_path:
            os.remove(path=lexeme.PAC_file_path)
            
            lexeme.PAC_file_path = None
            lexeme.save()
            return True
        else:
            return False
        

        
        
    def play_PAC(self, lexeme_identifier: str):
        # lexeme_attr = None
        lexeme: Lexeme = None

        if lexeme_identifier.isdigit():
            lexeme = Lexeme.select(Lexeme.string, Lexeme.PAC_file_path).get_by_id(lexeme_identifier)


            if not lexeme:
                raise LexemeNotFoundError(f"Lexeme with ID '{lexeme_identifier}' not found.")
        else:
            lexeme = Lexeme.select(Lexeme.string, Lexeme.PAC_file_path).where(Lexeme.string == lexeme_identifier).get_or_none()

            if not lexeme:
                raise LexemeNotFoundError(f"Lexeme with string '{lexeme_identifier}' not found.")
        
        

        if lexeme.PAC_file_path:
            play_audio_file(path=lexeme.PAC_file_path)
          
            return True
        
        return False

    