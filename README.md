# CusVoc App


CusVoc is a cross-platform application that is mainly intended for users who are trying to memorize words or phrases from their second languages. Words are stored locally via a __SQLite database__. CusVoc also sends requests to a __Public Vocabulary API__ in order to quickly access words and their definitions. Application is currently being implemented as a __Python Script__.

> This project is still under active development, see _Versioning_ section for more info.


## Libraries

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

## Versioning

During development we adhere to __Semantic Versioning__ which is a systematic way of developing software and keeping track of the changes made.


### 0.1.0

The very first release of __CusVoc Script__ is here! CusVoc now provides APIs for __Vocabulary Maintenance__ and __Vocabulary Testing__.

We are still testing the app by adding new words to our vocabulary to __detect possible bugs__ or __missing features__.

#### Release Date

28.08.2024



## Useful Links

Feel free to visit any of the following links for better understanding some terms commonly used in the application:

1) __Lexemes__ - https://www.studysmarter.co.uk/explanations/english/morphology/lexeme/
2) __Phrases vs Idioms__ - https://www.careerpower.in/idioms-and-phrases.html


