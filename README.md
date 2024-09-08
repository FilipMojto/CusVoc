# CusVoc App


CusVoc is a cross-platform application that is mainly intended for users who are trying to memorize words or phrases from their second languages. The application contains various mechanisms for effective Word Memorization, e. g. sentences or images. The application also utilizes various __Public Dictionary APIs__ for having a reliable source of data.  Application is currently being implemented in a form of __Python Script__.

> This project is still under active development, see _Versioning_ section for more info.


## Required Libraries

<!-- __Requests__ - for sending HTTP requests to the Public Dictionary API -->
<!-- nltk -->
1. __prettytable__ - for pretty-printing fetched results in tabular format in console
2. __python-Levenshtein__ - for calculating match ratio between strings during vocabulary testing

<!-- __platformdirs__ -->

## How to Install&Run

1. Make sure you have __Python__ (https://www.python.org/downloads/) and __Pip__ (https://pypi.org/project/pip/) installed. Also ensure their versions are satisfactory for the required libraries.
2. Install required __Python Libraries__ listed in _Libraries Sections_ using Pip if you don't have them already.
3. Download source files from _src_ subdirectory.
4. Run the main file _cusvoc.py_ using __Python Interpreter__.
5. (Optional) Enter command _-h_ or _--help_ to get a __guide__ to using the file.

## Repository Structure

### src

Contains all __Implementation Code__ of CusVoc application.

#### Files

1. _cusvoc.py_ - the main script file, provides commands for interacting with app
2. _vocabulary.py_ - contains API for maintaning personal vocabulary via class _Vocabulary_
3. _testvoc.py_ - contains API for __Vocabulary Testing__ via class _Tester_
4. _language.py_ - contain __constant data__ and __classes__ representing various entities in _English Language_

### model

Contains various images or files which represent the __Model__ of CusVoc application (__database ERD__, etc.). 

### data

Contains local data stored in __external files__. This is mainly the __personal vocabulary__ created by user.

### docs

Contains additional documentation to the project.

## Latest Release

During development we adhere to __Semantic Versioning__ which is a systematic way of developing software and keeping track of the changes made.


## 0.2.0

During development of this version we mainly focused on introducing many new features that would enhance the user's experience with the app. We also tested the update by adding some new entries while laying focus on vocabulary's CRUD operations and testvoc's TCP algorithm.

### New Features


1. __AudioPron__
    
    - Play pronunciation clip of your words thanks to an online dictionary API. You can also store these clips locally via _mp3 files_ to be able to play them offline.
    - __Relevant Commands:__ _'-l'_, _'-p'_ and _'-a'_

2. __Filtering Mechanism__

    - Filter entries or lexemes to be printed to the console thanks to using a new simple filtering system. 
    - __Relevant Commands:__ _'-e'_, _'-l'_ and _'--where'_

3. __For-Practice Entries:__

    - Flag __hard-to-learn entries__ with for-practice flag and you'll be able to put extra focus on them when testing.
    - __Relevant Commands:__ _'-e'_, _'-c'_, _'-t'_, _'--practice'_
4. __Imprting&Exporting Feature__
    - Another way of inserting entries into your vocabulary is by __importing an Entry File__. You can also __export__ your vocabulary into a file and import it elsewhere. PLease note, that these files should follow some popular tabular format, ideally __.tsv__.
    - __Relevant Commands:__ _'--import-file'_, _'--export-file'_, _'--delimiter'_



### Changes Made

1. _'--apend'_ command changed to _'--create'_
2. _'-c'_ command (originally as a shortcut for _'--category'_) changed to _'-ctg'_


### Bug Fixes

#### testvoc

1. Error in __TCP Algorithm__.
    
    - After testing all words an error appeared which made us change the way of how the algorithm works. The error should now be fixed.

### Release Date

08.09.2024

> For complete history and in-depth documentation of all releases of CusVoc App please check _releases.md_ file in _docs_ directory.





## Useful Links

Feel free to visit any of the following links for better understanding some terms commonly used in the application:

1) __Lexemes__ - https://www.studysmarter.co.uk/explanations/english/morphology/lexeme/
2) __Phrases vs Idioms__ - https://www.careerpower.in/idioms-and-phrases.html


