

# CusVoc App - Release History&Documentation

This document contains full history and documentation of releases of CusVoc application software. During sotware development we adhered to Semantic Versioning.

> This document only briefly describes releases and their features. For more in-depth guide and examples, please check _cusvoc_full_docs.md_ file located in _docs_.


## 0.2.0

During developing this version we mainly focused on introducing many new features that would enhance the user's experience with the app. We also tested the update by adding some new entries while laying focus on vocabulary's CRUD operations and testvoc's TCP algorithm.

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


## 0.1.0

The very first release of __CusVoc Script__ is here! CusVoc now provides APIs for __Vocabulary Maintenance__ and __Vocabulary Testing__.

We are still testing the app by adding new words to our vocabulary to __detect possible bugs__ or __missing features__.

### Release Date

28.08.2024

