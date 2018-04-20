import string
import nltk
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

# import codecs
# import sys
# sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

DBNAME = "poe_short_stories.db"

## Class definitions for accessing and representing data from poe_short_stories.db

class Story:

    def __init__(self, title):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        self.name = title

        sentence_lengths_statement = '''SELECT SentenceInStoryId, WordLength FROM Sentences WHERE ShortStory = "{}"'''.format(title)
        cur.execute(sentence_lengths_statement)
        self.sentence_lengths = cur.fetchall()

        ordered_sentence_lengths = sorted(self.sentence_lengths, key=lambda x: x[1])
        if len(ordered_sentence_lengths) % 2 == 0:
            second_index = len(ordered_sentence_lengths) // 2
            first_index = second_index - 1
            self.median_sent_length = (ordered_sentence_lengths[first_index][1] + ordered_sentence_lengths[second_index][1])/2
        else:
            index = len(ordered_sentence_lengths) // 2
            self.median_sent_length = ordered_sentence_lengths[index][1]

        proper_nouns_statement = '''SELECT ProperNouns FROM Sentences WHERE ShortStory = "{}"'''.format(title)
        cur.execute(proper_nouns_statement)
        proper_noun_tups = cur.fetchall()
        all_proper_nouns = []
        for list in proper_noun_tups:
            all_proper_nouns += list[0].split(", ")
        proper_nouns = []
        for noun in all_proper_nouns:
            if noun != "":
                proper_nouns.append(noun)
        freq_dist = nltk.FreqDist(proper_nouns)
        self.proper_nouns = freq_dist.most_common(10)

        year_statement = '''SELECT YearPublished FROM ShortStories WHERE StoryName="{}"'''.format(title)
        cur.execute(year_statement)
        self.year = cur.fetchone()[0]
        conn.close()

    def __str__(self):
        string_rep = "{}; published in {}; {} sentences long".format(self.name, self.year, len(self.sentence_lengths))
        return string_rep

    def fetch_first_ten_sentences(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        first_statement = '''
            SELECT Sentence
            FROM Sentences
            WHERE ShortStory = '{}'
            LIMIT 10
        '''.format(self.name)
        cur.execute(first_statement)
        first_ten_sentences = cur.fetchall()
        return first_ten_sentences

    def make_story_sentence_graph(self):
        print("Creating line graph using Plotly...")
        sentence_pos = []
        sentence_length = []
        for tup in self.sentence_lengths:
            sentence_pos.append(tup[0])
            sentence_length.append(tup[1])
        trace0 = go.Scatter(
            x = sentence_pos,
            y = sentence_length,
            name = 'Sentence_Length',
            line = dict(
                color = ('rgb(18, 10, 135)'),
                width = 3)
        )
        data = [trace0]
        layout = dict(title = 'Length of Each Sentence in "{}"'.format(self.name),
            xaxis = dict(title = 'Sentence Position in Story'),
            yaxis = dict(title = 'Sentence Length in Words'),
        )
        fig = dict(data=data, layout=layout)
        py.plot(fig, filename='styled-line')
        pass

    def make_proper_nouns_chart(self):
        noun = []
        frequency = []
        for tup in self.proper_nouns:
            noun.append(tup[0])
            frequency.append(tup[1])
        trace0 = go.Bar(
            x= noun,
            y= frequency,
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                color='rgb(8,48,107)',
                width=1.5,
                    )
                ),
            opacity=0.6
            )
        data = [trace0]
        layout = go.Layout(
            title='Ten Most Common Proper Nouns in "{}"'.format(self.name),
        )
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename='text-hover-bar')
        pass

class Collection:

    def __init__(self, name, list_of_story_instances):
        self.collection_name = name
        self.num_of_stories = len(list_of_story_instances)
        self.story_tups = []
        for story in list_of_story_instances:
            story_tup = (story.name, story.year, story.median_sent_length)
            self.story_tups.append(story_tup)

    def make_collection_sentence_graph(self):
        print("Creating line graph using Plotly...")
        story_tups_sorted_alphabet = sorted(self.story_tups, key=lambda x: x[0])
        story_tups_sorted_year = sorted(story_tups_sorted_alphabet, key=lambda x: x[1])
        year_story = []
        median_length = []
        for tup in story_tups_sorted_year:
            x_string = '{} ("{}")'.format(tup[1], tup[0])
            year_story.append(x_string)
            median_length.append(tup[2])
        trace0 = go.Scatter(
            x = year_story,
            y = median_length ,
            name = 'Median Sentence Lengths',
            line = dict(
                color = ('rgb(18, 10, 135)'),
                width = 3)
        )
        data = [trace0]
        layout = dict(title = "Median Sentence Length for Edgar Allan Poe Stories by Year",
            xaxis = dict(title = 'Year (Story Published)'),
            yaxis = dict(title = 'Median Sentence Length'),
        )
        fig = dict(data=data, layout=layout)
        py.plot(fig, filename='styled-line')
        pass

class Entry:

    def __init__(self, entry_tup):
        self.word_defined = entry_tup[0]
        self.part_of_speech = entry_tup[1]
        definition_string = entry_tup[2]
        self.definitions = definition_string.split("; ")
        self.date = entry_tup[3]
        self.pronunciation = entry_tup[4]

    def __str__(self):
        definitions = []
        for defin in self.definitions:
            definitions.append(defin)
        definition_string = "\n".join(definitions)
        string_rep = '''Word Defined: {}
Part of Speech: {}
Definitions:
{}
Origin Date: {}
Pronunciation: {}'''.format(self.word_defined, self.part_of_speech, definition_string, self.date, self.pronunciation)
        return string_rep

class Word:

    def __init__(self, word):

        self.word = word

        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        word_statement = "SELECT Frequency FROM LongestWords WHERE Word = '{}'".format(word)
        cur.execute(word_statement)
        self.frequency = cur.fetchone()[0]

        entries_statement = '''
        SELECT WordDefined, PartOfSpeech, Definitions, Date, Pronunciation
        FROM Entries
            WHERE Word = '{}'
        '''.format(word)
        cur.execute(entries_statement)
        self.entries = []
        for entry in cur.fetchall():
            self.entries.append(Entry(entry))

        conn.close()

    def __str__(self):
        string_rep = "{}: times longest: {}; dictionary entries: {}".format(self.word, self.frequency, len(self.entries))
        return string_rep

    def display_entries_info(self):
        entries_string_rep = '* Entries for "{}" and related words from Meriam-Webster.com *\n\n'.format(self.word)
        entry_num = 0
        for entry in self.entries:
            entry_num += 1
            entries_string_rep += "| Entry {} | \n{}".format(entry_num, entry.__str__())
        return entries_string_rep

    def collect_longest_word_appearances(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        appear_statement = '''
            SELECT ShortStory, SentenceInStoryId, Sentence
            FROM Sentences
            JOIN LongestWordAppearances
	           ON Sentences.Id=LongestWordAppearances.SentenceId
            WHERE LongestWordAppearances.Word = "{}"
        '''.format(self.word)
        cur.execute(appear_statement)
        appear_tups = cur.fetchall()
        conn.close()
        appear_string = '// Sentences in which "{}" appears as one of the longest words //\n\n'.format(self.word)
        appear_num = 0
        for tup in appear_tups:
            appear_num += 1
            appear_string += '{}) "{}", sentence {}: {}\n'.format(appear_num, tup[0], tup[1], tup[2])
        return appear_string

# Functions to collect data

def prepare_stories_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    stories_statement = '''
        SELECT StoryName FROM ShortStories
    '''
    cur.execute(stories_statement)
    story_names = cur.fetchall()
    conn.close()
    story_instances = []
    for story in story_names:
        story_instances.append(Story(story[0]))
    return story_instances

def prepare_words_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    words_statement = '''
        SELECT Word FROM LongestWords
    '''
    cur.execute(words_statement)
    words = cur.fetchall()
    conn.close()
    word_instances = []
    for word in words:
        word_instances.append(Word(word[0]))
    return word_instances

# Creating a pie graph of centuries for a presentation option

def make_pie_graph_of_centuries(list_of_word_instances):
    entries = []
    for word in list_of_word_instances:
        entries += word.entries
    centuries = []
    for entry in entries:
        date = entry.date
        if "circa" in date:
            date = date.replace("circa", "").strip()
        if len(date) == 4:
            date_num = int(date)
            if date_num >= 1800 and date_num < 1900:
                new_date = "19th century"
            elif date_num >= 1700 and date_num < 1800:
                new_date = "18th century"
            elif date_num >= 1600 and date_num < 1700:
                new_date = "17th century"
            elif date_num >= 1500 and date_num < 1600:
                new_date = "16th century"
            elif date_num >= 1400 and date_num < 1500:
                new_date = "15th century"
            centuries.append(new_date)
        else:
            centuries.append(date)

    freq_dist = nltk.FreqDist(centuries)
    labels = []
    values = []
    for sample in freq_dist.most_common():
        labels.append(sample[0])
        values.append(sample[1])

    trace = go.Pie(labels=labels, values=values)
    py.plot([trace], filename='basic_pie_chart')

    pass

def validate_entry_length(entry):
    terms = entry.split()
    if len(terms) == 0:
        print("You did not enter anything. Try again.")
        return False
    elif len(terms) > 1:
        print("You entered too many terms. Try again.")
        return False
    else:
        return True

def validate_number_option(entry, length):
    integer = True
    for char in entry:
        if char not in string.digits:
            integer = False
    if integer == False or integer not in range(1, length):
        print("You did not enter a valid word number. Try again.")
        return False
    else:
        return True

## Interactive Prompt

print("SI 507 Final Project")
print("Analyzing Edgar Allan Poe Short Stories")
print("by Sam Sciolla")
print('''("Tear up the planks!" - The Tell-Tale Heart)''')

in_progress = True
while in_progress:
    entry = input('''\n* Main Menu *
Your main options are to enter "Stories" and "Collection".
You can also enter "Help" to learn more about the options or "Quit" to exit the program
// What will you do first? //
>>> ''')
    result = validate_entry_length(entry)
    if result == True:
        if entry not in ["collection", "stories", "help", "quit"]:
            print("You did not enter a valid option. Try again.")
        else:
            if entry == "help": #RETURN TO THIS
                print('''
// Option 1: Stories //
// Option 2: Collection //
                ''')
            elif entry == "quit":
                print("THE END")
                in_progress = False
            else:
                stories = prepare_stories_data()
                if entry == "stories":
                    stay_at_stories = True
                    while stay_at_stories:
                        print("\n* Short Stories *")
                        story_num = 0
                        for story in stories:
                            story_num += 1
                            print('{}) {}'.format(story_num, story.__str__()))
                        print('''
On Wikisource, there are {} short stories available by Edgar Allan Poe.
Here you can read the first 10 sentences of each story and view graphs about sentence_lengths and proper nouns.
Enter the number from the list above that corresponds to the story you want to learn more about.
You can also enter "Menu" to return to the main menu.
// What will you do next? //'''.format(len(stories)))
                        entry = input(">>> ")
                        result = validate_entry_length(entry)
                        if result == True:
                            if entry == "menu":
                                stay_at_stories = False
                            else:
                                num_result = validate_number_option(entry, len(stories))
                                if num_result == True:
                                    index = int(entry) - 1
                                    story = stories[index]
                                    stay_at_specific_story = True
                                    while stay_at_specific_story:
                                        print('''\n* {} *'''.format(story.name))
                                        print("First Ten Sentences:")
                                        for sentence in story.fetch_first_ten_sentences():
                                            print(*sentence)
                                        print('''
You can view a line graph tracking how sentence lengths change over the course of the story.
Or you can view a bar chart showing the 10 most common proper nouns in the story.
Your main options are to enter "Sentences" or "Nouns".
Or you can enter "Stories" to return to the Short Stories menu.
// What will you do next? //''')
                                        entry = input(">>> ")
                                        result = validate_entry_length(entry)
                                        if result == True:
                                            if entry not in ["sentences", "nouns", "stories"]:
                                                print("You did not enter a valid option. Try again.")
                                            else:
                                                if entry == "stories":
                                                    stay_at_specific_story = False
                                                elif entry == "sentences":
                                                    story.make_story_sentence_graph()
                                                elif entry == "nouns":
                                                    story.make_proper_nouns_chart()
                elif entry == "collection":
                    poe_collection = Collection("Short Stories by Edgar Allan Poe", stories)
                    stay_at_collection = True
                    while stay_at_collection:
                        print("\n* Collection *")
                        print('''{}
{} total stories
You can see data related to words that are commonly the longest words.
Or you can view a graph showing how stories' median sentence length changed over time.\n
Your main options are to enter "Words" or "Sentences".
You can also enter "Menu" to return to the starting menu.
// What will you do next? //'''.format(poe_collection.collection_name, poe_collection.num_of_stories))
                        entry = input(">>> ")
                        result = validate_entry_length(entry)
                        if result == True:
                            if entry == "menu":
                                stay_at_collection = False
                            elif entry not in ["words", "sentences"]:
                                print("You did not enter a valid option. Try again.")
                            else:
                                if entry == "sentences":
                                    print("Creating a line graph using Plotly...")
                                    poe_collection.make_collection_sentence_graph()
                                elif entry == "words":
                                    longest_words = prepare_words_data()
                                    stay_at_words = True
                                    while stay_at_words == True:
                                        print("\n* Longest Words *")
                                        print('''The 100 words that are most commonly the longest word (or tied for the longest) in Poe's sentences have been identified.
You can explore a list of the words and details about them, including frequencies, definitions, and sentences.
Or you can view a pie chart displaying the distribution of centuries the words originated in.
Your main options are to enter "List" or "Centuries".
You can also enter "Collection" to return to the previous menu.
// What will you do next? //''')
                                        entry = input(">>> ")
                                        result = validate_entry_length(entry)
                                        if result == True:
                                            if entry == "collection":
                                                stay_at_words = False
                                            elif entry not in ["list", "centuries"]:
                                                print("You did not enter a valid option. Try again.")
                                            else:
                                                if entry == "centuries":
                                                    make_pie_graph_of_centuries(longest_words)
                                                elif entry == "list":
                                                    stay_at_list = True
                                                    while stay_at_list:
                                                        print("\n* List of Longest Words *")
                                                        word_number = 0
                                                        for word in longest_words:
                                                            word_number += 1
                                                            print('{}) {}'.format(word_number, word.__str__()))
                                                        print('''
You can view the sentences from Poe's short stories in which a word was one of the longest words.
Or you can see dictionary entries for the word and simliar words.
Your main options are to enter "Sentences" or "Dictionary", followed by the word's number in the above list.
You can also enter "Words" to return to the previous menu.
// What will you do next? //''')
                                                        entry = input(">>> ")
                                                        terms = entry.split()
                                                        option = terms[0].lower()
                                                        if option not in ["words", "sentences", "dictionary"]:
                                                            print("You did not enter a valid option. Try again.")
                                                        else:
                                                            if option == "words": # What about "word something"?
                                                                stay_at_list = False
                                                            else:
                                                                if len(terms) != 2:
                                                                    print("You entered the wrong number of terms. Try again.")
                                                                else:
                                                                    num_result = validate_number_option(terms[1], 100)
                                                                    if result == True:
                                                                        index = int(terms[1]) - 1
                                                                        if option == "dictionary":
                                                                            print(longest_words[index].display_entries_info())
                                                                        elif option == "sentences":
                                                                            print(longest_words[index].collect_longest_word_appearances())
