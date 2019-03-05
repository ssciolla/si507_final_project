## SI 507 Final Project ReadMe
## Basic Text Analysis of Edgar Allan Poe Short Stories
#### by Sam Sciolla
#### GSI: Deahan Yu
#### Section: Monday, 1 p.m.

Repository contents:
final_project.py
final_project_interactive.py
final_projects_tests.py
final_project_cache.json
stories.json
poe_short_stories.db
help.txt
requirements.txt

### 1. Data Sources

My Final Project takes advantage of two data sources: Wikisource and Merriam-Webster's Collegiate Dictionary with Audio API.

For Wikisource, I collected links to all of the short stories by Edgar Allan Poe, listed in the "Individual Stories" table at
https://en.wikisource.org/wiki/Author:Edgar_Allan_Poe, and then crawled through them to scrape the full text of each story. Full html from each page was cached, with the page's URL serving as the dictionary key.

For Merriam-Webster, I made requests to the API for the 100 words that are most frequently the longest word in sentences from Poe's
short stories. To do this, I first I applied for and obtained an API key by registering at Merriam-Webster.com's Developer Center (https://www.dictionaryapi.com/register/index.htm). I found documentation for the Collegiate Dictionary API at https://www.dictionaryapi.com/products/api-collegiate-dictionary.htm. I created a base URL by taking the stem of the provided URL (https://www.dictionaryapi.com/api/v1/references/collegiate/xml/) and concatenating the desired word and then "?". I then passed the URL to
the requests.get method with a parameters dictionary containing only the API key. Responses came back in XML, which I parsed using Beautiful Soup (though I had to pip install lxml to do so). Full XML was cached with a unique request string (without the API key) serving as the dictionary key.

The Merriam-Webster API key needs to be added to a file called secrets.py with the variable name "merriam_webster_api_key" for the program to execute properly. Upon request, I can provide my API key to a grader.

### 2. Other Information Needed

Both final_project.py and final_project_interactive.py use the Natural Language Toolkit (nltk) module. Depending on your programming environment, you may need to download particular packages (e.g. "punkt"). If you do, put a line like the following at the top of your program on the line after "import nltk", changing the name of the string as necessary: "nltk.download('averaged_perceptron_tagger')"

If you have never used the Plotly graphing service before, you will need to go through some extra steps to use the module in Python, including creating a free account. Follow the instructions at this link: https://plot.ly/python/getting-started/

### 3. Important Functions and Classes

The core functionality for my final project is implemented through two files: final_project.py and final_project_interactive.py. A few key
functions and classes from each are described below.

#### final_project.py

Calls to all major functions are contained at the bottom of the file in a section with a comment entitled "Main Program".

Function: rerun_or_load
Valid inputs: "rerun" or "load"
Description: This is a program flow control function that either uses raw HTML from the cache (or through requests) to do text analysis or loads the results from a file called stories.json. The first ("rerun") takes the raw data and generates a dictionary that contains the year the story was published, full text of the story, the story broken into sentences, and then a list with statistics later added to the database (see create_data_from_sentences function) and writes it to stories.json. The keys of the dictionary are the names of stories. The program has been saved with the load "input", but those wanting to construct stories.json may want to use "rerun".

Function: find_common_longest_words
Valid input: the dictionary containing story data
Description: This function collects words identified as the longest for each sentence from all stories in the dictionary (saved to stories.json) and then adds them to a list if they are six characters or longer. Using the Natural Language Toolkit, a frequency distribution is done on this list, and then the 100 most common words are identified. For each of the 100 words, a request is made to the Merriam-Webster API, and the resulting XML is parsed to find dictionary entries for the word or a related word (some words have multiple) and details about definitions, parts of speech, date of origin, and pronunciation (see gather_dictionary_data_for_word function). The data is saved in a dictionary, with the keys corresponding to each word.

#### final_project_interactive.py

Class: Story
Valid input to constructor: a string, the title of one of Poe's short story
The Story class uses the poe_short_stories.db database to pull together data related to each story and define actions users would want to take related to a story. The instance variables include name (the title of the story), sentence_lengths (the position and length in words of each sentence), median_sent_length (the median sentence length in words, calculated using the previous instance variable), and proper_nouns (the ten most common proper nouns, as identified using a frequency distribution on all proper nouns identified in the story). The methods include a basic string method for browsing purposes, fetch_first_ten_sentences (which returns the first ten sentences of the story), make_story_sentence_graph (which uses Plotly to create a line graph with each sentences's word length and position in the story, relying on the sentence_lengths variable), and make_proper_nouns_chart (which uses Plotly to create a bar chart showing how many times the most common nouns appear in each story). The Story class is also used by a Collection class to create a Plotly line graph of stories' median sentence lengths.

Class: Word
Valid input to constructor: a string, an English word
The Word class uses the poe_stories.db database to pull together data related to each word and define actions users might want to take related to each word. Its instance variables are word (the name of the word), frequency (the number of times it is the longest word or tied for the longest word in one of Poe's sentences), and entries (a list containing instances of another class, Entry, which structures data about each dictionary entry related to a word). The methods include a basic string method for browsing purposes, display_entries_info (which returns a neatly formatted list of dictionary entries) and collect_longest_word_appearances (which finds all appearances in sentences of the word when it is one of the longest words and returns them neatly formatted).

### 4. User Guide

The first step is to run the final_project_interactive.py file in your command line prompt. After, you will be presented with a series of menu, with explanations about your options provided at each menu. The hierarchy of the system is laid out below. Lines with stars before them represent possible choices, with the term in quotation marks after representing what entry is needed to reach the corresponding menu from the menu above. Entries are not case sensitive. Lines without stars indicate content that will appear automatically in the menu indicated by a star directly above it. To return to the previous menu, enter the term in parentheses at the next highest level. To exit the program completely, return to the Main Menu and enter "Quit".

#### Program Hierarchy

* Main Menu ("Menu")
     * Short Stories ("Stories")
          Numbered List of Short Stories
          * "[Specific Short Story Name]" ("[#]")
               First Ten Sentences
               * Line Graph of Sentence Lengths ("Sentences")
               * Bar Chart of Proper Nouns ("Nouns")
     * Collection ("Collection")
          * Longest Words ("Words")
               * Pie Chart of Century Origins of Longest Words ("Centuries")
               * List of Longest Words ("List")
                    List of Longest Words
                    * Appearances of Longest Word in Sentences from Short Stories ("Sentences [#]")
                    * Dictionary entries for Specific Longest Word ("Dictionary [#]")
               * Line Graph of Short Stories' Median Sentence Length by Year ("Sentences")
