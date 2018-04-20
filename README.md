SI 507 Final Project ReadMe
Basic Text Analysis of Edgar Allan Poe Short Stories
by Sam Sciolla
GSI: Deahan Yu
Section: Monday, 1 p.m.

● Data sources used, including instructions for a user to access the data sources (e.g., API
keys or client secrets needed, along with a pointer to instructions on how to obtain these
and instructions for how to incorporate them into your program (e.g., secrets.py file
format))
1. Data Sources

Wikisource
https://en.wikisource.org/wiki/Author:Edgar_Allan_Poe

Merriam-Webster Collegiate Dictionary API
API key: included in submission to Canvas

The API key needs to be added to a file called secrets.py with the variable name merriam_webster_api_key

● Any other information needed to run the program (e.g., pointer to getting started info for plotly)
2. Other Information Needed
Natural Language Toolkit

Plotly

● Brief description of how your code is structured, including the names of significant data
processing functions (just the 2-3 most important functions--not a complete list) and
class definitions. If there are large data structures (e.g., lists, dictionaries) that you create
to organize your data for presentation, briefly describe them.
3. Important Functions and Classes

The functionality for my final project includes two main files: final_project.py and final_project_interactive.py. The key
functions and classes from each are described in detail below.

final_project.py

Structural functions
-

Functions that analyze and process data
-

Functions that access data using requests
- extract_poe_story()
- gather_dictionary_data_for_word()

final_project_interactive.py

Story class
Collection class
Word class
Entry class

● Brief user guide, including how to run the program and how to choose presentation
options.
4. User Guide
entries are not case sensitive

Interactive Hierarchy

Main Menu
  * Short Stories ("Stories")
    * Numbered List of Short Stories ("[#]")
      "[Specific Short Story Name]"
      First Ten Sentences
      * Line Graph of Sentence Lengths ("Sentences")
      * Bar Chart of Proper Nouns ("Nouns")
  * Collection ("Collection")
    * Longest Words ("Words")
      * Pie Chart of Century Origins of Longest Words ("Centuries")
      * More Details about Longest Words
        List of Longest Words
        * Appearances of Longest Word in Sentences from Short Stories ("Sentences [#]")
        * Dictionary entries for Specific Longest Word ("Dictionary [#]")
    * Line Graph of Short Stories' Median Sentence Length by Year ("Sentences")
