from bs4 import BeautifulSoup
import json
import requests
import codecs
import sys
import nltk
import string
import secrets
import sqlite3
# nltk.download('averaged_perceptron_tagger')

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

CACHE_FNAME = "final_project_cache.json"
API_KEY = secrets.merriam_webster_api_key
DBNAME = 'poe_short_stories.db'

# Caching setup
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

# Making unique request string for Merriam-Webster API caching
def make_unique_request_string(base_url, params_diction, private_keys=["key"]):
    sorted_parameters = sorted(params_diction.keys())
    fields = []
    for parameter in sorted_parameters:
        if parameter not in private_keys:
            fields.append("{}-{}".format(parameter, params_diction[parameter]))
    return base_url + "&".join(fields)

# Make the request and cache the new data, or get cached data
def make_request_using_cache(url, params=None):
    if params != None:
        cache_url = make_unique_request_string(url, params)
    else:
        cache_url = url
    if cache_url in CACHE_DICTION.keys():
        print("Getting cached data...")
        return CACHE_DICTION[cache_url]
    else:
        print("Making a request for new data...")
        if params != None:
            response = requests.get(url, params)
            CACHE_DICTION[cache_url] = response.text
        else:
            response = requests.get(url)
            CACHE_DICTION[cache_url] = response.text
        dumped_json_cache = json.dumps(CACHE_DICTION, indent=4)
        file_open = open(CACHE_FNAME,"w")
        file_open.write(dumped_json_cache)
        file_open.close()
        return CACHE_DICTION[cache_url]

def extract_poe_story(url_ending):
    url = "https://en.wikisource.org" + url_ending
    data = make_request_using_cache(url)
    html = BeautifulSoup(data, "html.parser")
    story = html.find("div", class_="mw-parser-output")
    return story

def join_paragraphs(html):
    all_paragraphs = html.find_all("p")
    text_of_paragraphs = []
    index = 0
    for para in all_paragraphs:
        raw_text = para.text.strip()
        if index < 6: # Hardcoded by necessity
            accum = 0
            for char in raw_text:
                if char in string.ascii_letters:
                    if char not in string.ascii_uppercase:
                        if "publish" not in raw_text.lower():
                            text_of_paragraphs.append(raw_text)
                            break
                        elif "Von Kempelen" in raw_text:
                            text_of_paragraphs.append(raw_text)
                            break

                elif char not in string.printable:
                    text_of_paragraphs.append(raw_text)
                    break
                accum += 1
                if accum == len(raw_text):
                    print(raw_text)
        elif "public domain" not in raw_text:
            text_of_paragraphs.append(raw_text)
        index += 1
    story_text = "   ".join(text_of_paragraphs)
    return story_text

def crawl_for_poe_stories():
    # Get Poe links
    poe_link = "https://en.wikisource.org/wiki/Author:Edgar_Allan_Poe"
    data = make_request_using_cache(poe_link)
    html = BeautifulSoup(data, "html.parser")
    story_table = html.find("table", class_="wikitable sortable").find_all("tr")
    story_dictionary = {}
    for line in story_table[1:]:
        tds = line.find_all("td")
        title = tds[0].find("a").text
        story_dictionary[title] = {"url ending": tds[0].find("a")["href"], "year": tds[1].text}

    tricky_stories = ["The Fall of the House of Usher", "The Journal of Julius Rodman", "Morella", "Eleonora", "The Black Cat",
                      "The Facts in the Case of M. Valdemar"]
    for story in story_dictionary.keys():
        url_ending = story_dictionary[story]["url ending"]
        if story not in tricky_stories:
            story_dictionary[story]["full text"] = join_paragraphs(extract_poe_story(url_ending))
        else:
            if story != "The Journal of Julius Rodman":
                versions_html = extract_poe_story(url_ending)
                if story == "The Black Cat":
                    index = 3
                else:
                    index = 1
                specific_version = versions_html.find_all("li")[index]
                new_url_ending = specific_version.find("a")["href"]
                story_dictionary[story]["url ending"] = new_url_ending
                year_index = specific_version.text.find("18")
                story_dictionary[story]["year"] = specific_version.text[year_index:year_index + 4]
                story_dictionary[story]["full text"] = join_paragraphs(extract_poe_story(new_url_ending))
            else:
                chapters_html = extract_poe_story(url_ending)
                all_links_html = chapters_html.find_all("ul")[1].find_all("li")
                story_dictionary[story]["url ending"] = []
                full_text = ""
                for li in all_links_html:
                    chapter_url_ending = str(li.find("a")["href"])
                    story_dictionary[story]["url ending"].append(chapter_url_ending)
                    chapter_text = join_paragraphs(extract_poe_story(chapter_url_ending))
                    full_text = full_text + "   " + chapter_text
                story_dictionary[story]["full text"] = full_text
    return story_dictionary

def chunk_story_into_sentences(title, story_text):
    text = story_text.replace("\n"," ").replace("\u2060"," ").replace("\u2014", " ")
    sentences = nltk.sent_tokenize(text)
    actual_sentences = []
    for sentence in sentences:
        accum = 0
        for char in sentence:
            accum += 1
            if char in string.ascii_letters or char in string.digits:
                actual_sentences.append(sentence)
                break
    sentences = actual_sentences
    return sentences

def create_data_from_sentences(sentences):
    story_data = []
    accum = 0
    for sentence in sentences:
        accum += 1
        sentence_data = []
        # Sentence number
        sentence_data.append(accum)
        # Sentence
        sentence_data.append(sentence)
        # Length in characters
        sentence_data.append(len(sentence))
        # Last character
        if sentence[-1] == '"' and sentence[-2] in string.punctuation:
            sentence_data.append(sentence[-2])
        else:
            sentence_data.append(sentence[-1])
        tokens = nltk.word_tokenize(sentence)
        words = []
        for token in tokens:
            if token not in string.punctuation and token != "``" and token != "''" and len(token) != 0:
                words.append(token)
        # Length of sentence in words
        sentence_data.append(len(words))
        # List of proper nouns
        tagged_tokens = nltk.pos_tag(words)
        proper_nouns = []
        for token in tagged_tokens:
            if token[1] == "NNP" or token[1] == "NNPS" or token[0] in ["AGATHOS", "OINOS"]:
                proper_nouns.append(token[0])
        sentence_data.append(proper_nouns)
        # Longest word(s)
        longest_words = []
        current_longest_word = ''
        for word in words:
            if word not in proper_nouns and "-" not in word:
                if len(word) > len(current_longest_word):
                    longest_words = []
                    longest_words.append(word.lower())
                    current_longest_word = word
                elif len(word) == len(current_longest_word) and word not in longest_words:
                    longest_words.append(word.lower())
        if current_longest_word == '':
            longest_words = []
        sentence_data.append(longest_words)
        story_data.append(sentence_data)
    return story_data

def rerun_or_load(mode):
    if mode == "rerun":
        poe_stories = crawl_for_poe_stories()
        for story in poe_stories.keys():
            sentences = chunk_story_into_sentences(story, poe_stories[story]["full text"])
            poe_stories[story]["sentences"] = sentences
            poe_stories[story]["story data"] = create_data_from_sentences(poe_stories[story]["sentences"])
        stories_file_open = open("stories.json", "w")
        stories_file_open.write(json.dumps(poe_stories, indent=4))
        stories_file_open.close()
        return poe_stories
    elif mode == "load":
        stories_file_open = open("stories.json", "r")
        poe_stories = json.loads(stories_file_open.read())
        return poe_stories

# Processing XML and organizing data from Merriam-Webster API for longest words
def compare_headword_to_word(headword, word):
    if headword == word:
        return (True, None)
    else:
        if headword[:-1] in word and len(headword) >= (len(word) - 2):
            return (True, headword)
        else:
            return (False,)

def gather_dictionary_data_for_word(word):
    params = {"key": API_KEY}
    url = "https://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}?".format(word)
    data = make_request_using_cache(url, params)
    xml = BeautifulSoup(data, "xml")
    entries = xml.find_all("entry")
    data_for_word = []
    for entry in entries:
        hw = entry.find("hw").text
        headword = ""
        for char in hw:
            if char not in "*[]" and char not in string.digits:
                headword += char
        result_tup = compare_headword_to_word(headword, word)
        if result_tup[0] == True:
            # definitions
            dts = entry.find_all("dt")
            definitions = []
            for dt in dts:
                definitions.append(dt.text)
            if len(definitions) > 0:
                if entry.find("fl") != None:
                    part_of_speech = entry.find("fl").text
                else:
                    part_of_speech = None
                # word defined
                if result_tup[1] == None:
                    word_defined = word
                else:
                    word_defined = headword

                # date
                if entry.find("date") != None:
                    date = entry.find("date").text
                else:
                    date = None
                # pronunciation
                if entry.find("pr") != None:
                    pronunciation = entry.find("pr").text
                else:
                    pronunciation = None
                entry_data = [word_defined, part_of_speech, definitions, date, pronunciation]
                data_for_word.append(entry_data)
            # else:
            #     print("No definitions? " + word)
        else:
            print(headword + " is not exactly " + word)
    return data_for_word

def find_common_longest_words(story_dictionary):
    longest_words = []
    for story in poe_stories:
        story_data = poe_stories[story]["story data"]
        for sentence_data in story_data:
            for longest_word in sentence_data[-1]:
                if len(longest_word) >= 5: # Need to note this decision somewhere
                    longest_words.append(longest_word)
    freq_dist = nltk.FreqDist(longest_words)
    most_common = freq_dist.most_common(100)
    dictionary_of_words = {}
    for word in most_common:
        data = gather_dictionary_data_for_word(word[0])
        if len(data) == 0:
            print(word)
            print(data)
        dictionary_of_words[word[0]] = {}
        dictionary_of_words[word[0]]["data"] = data
        dictionary_of_words[word[0]]["frequency"] = word[1]
    return dictionary_of_words

## Functions to setup database

def init_poe_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        conn.close()
    except:
        print("Unable to create or connect to poe_short_stories.db database.")

def create_short_stories_table(short_stories):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    table_name = "ShortStories"
    drop_statement = '''
        DROP TABLE IF EXISTS '{}';
    '''.format(table_name)
    cur.execute(drop_statement)
    conn.commit()
    stories_statement = '''
        CREATE TABLE '{}' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'StoryName' TEXT NOT NULL,
            'YearPublished' INT NOT NULL
            );
    '''.format(table_name)
    conn.execute(stories_statement)

    for title in short_stories.keys():
        story_name = title
        year_published = short_stories[title]["year"]
        story_tup = (None, story_name, year_published)
        story_pop_statement = "INSERT INTO '{}' ".format(table_name)
        story_pop_statement += "VALUES (?, ?, ?)"
        cur.execute(story_pop_statement, story_tup)
    conn.commit()
    conn.close()

def create_sentences_table(short_stories):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    drop_statement = '''
        DROP TABLE IF EXISTS 'Sentences';
    '''
    cur.execute(drop_statement)
    conn.commit()
    sentences_statement = '''
        CREATE TABLE 'Sentences' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'ShortStory' TEXT NOT NULL,
            'ShortStoryId' INT NOT NULL,
            'SentenceInStoryId' INT NOT NULL,
            'Sentence' TEXT NOT NULL,
            'CharLength' INT NOT NULL,
            'LastChar' TEXT NOT NULL,
            'WordLength' INT NOT NULL,
            'ProperNouns' TEXT,
            'LongestWords' TEXT
            );
    '''
    conn.execute(sentences_statement)

    for story in short_stories.keys():
        for sentence_data in short_stories[story]["story data"]:
            short_story = story
            sentence_number = sentence_data[0]
            sentence = sentence_data[1]
            char_length = sentence_data[2]
            last_char = sentence_data[3]
            word_length = sentence_data[4]
            proper_nouns = ", ".join(sentence_data[5])
            longest_words = ", ".join(sentence_data[6])
            sentence_tup = (None, short_story, short_story, sentence_number, sentence, char_length, last_char, word_length, proper_nouns, longest_words)
            sentence_pop_statement = "INSERT INTO 'Sentences' "
            sentence_pop_statement += '''VALUES (?, ?, (SELECT Id FROM ShortStories WHERE StoryName=?), ?, ?, ?, ?, ?, ?, ?)'''
            cur.execute(sentence_pop_statement, sentence_tup)
    conn.commit()
    conn.close()
    pass

def create_longest_words_table(dictionary):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    drop_statement = '''
        DROP TABLE IF EXISTS 'LongestWords';
    '''
    cur.execute(drop_statement)
    longest_words_statement = '''
        CREATE TABLE 'LongestWords' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Word' TEXT NOT NULL,
            'Frequency' INT NOT NULL
            );
    '''
    cur.execute(longest_words_statement)

    longest_word_tups = []
    for word in dictionary.keys():
        frequency = dictionary[word]["frequency"]
        insertion = (None, word, frequency)
        longest_word_pop_statement = "INSERT INTO 'LongestWords' "
        longest_word_pop_statement += '''VALUES (?, ?, ?)'''
        cur.execute(longest_word_pop_statement, insertion)
    conn.commit()
    conn.close()
    pass

def create_entries_table(dictionary):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    drop_statement = '''
        DROP TABLE IF EXISTS 'Entries';
    '''
    cur.execute(drop_statement)
    entries_statement = '''
        CREATE TABLE 'Entries' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Word' TEXT NOT NULL,
            'WordDefined' TEXT NOT NULL,
            'PartOfSpeech' TEXT,
            'Definitions' TEXT,
            'Date' TEXT,
            'Pronunciation' TEXT,
            'LongestWordId' INT NOT NULL
            );
    '''
    cur.execute(entries_statement)

    for word in dictionary.keys():
        for entry in dictionary[word]["data"]:
            word_defined = entry[0]
            part_of_speech = entry[1]
            definition_elem = entry[2]
            if definition_elem == None:
                definitions = None
            else:
                if len(definition_elem) > 1:
                    definitions = []
                    accum = 1
                    for definition in definition_elem:
                        definitions.append("{}) {}".format(accum, definition))
                        accum += 1
                    definitions = "; ".join(definitions)
                else:
                    definitions = "1) " + definition_elem[0]
            date = entry[3]
            pronunciation = entry[4]
            entry_tup = (None, word, word_defined, part_of_speech, definitions, date, pronunciation, word)
            entry_pop_statement = "INSERT INTO 'Entries' "
            entry_pop_statement += '''VALUES (?, ?, ?, ?, ?, ?, ?,
            (SELECT Id FROM LongestWords WHERE Word = ?))
            '''
            cur.execute(entry_pop_statement, entry_tup)
    conn.commit()
    conn.close()
    pass

def create_joint_table(stories_dict, words_dict):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    table_name = "LongestWordAppearances"
    drop_statement = '''
        DROP TABLE IF EXISTS '{}';
    '''.format(table_name)
    cur.execute(drop_statement)
    joint_table_statement = '''
        CREATE TABLE '{}' (
            'WordId' INT NOT NULL,
            'Word' TEXT NOT NULL,
            'StoryId' INT NOT NULL,
            'StoryName' TEXT NOT NULL,
            'SentenceId' INT NOT NULL
            );
    '''.format(table_name)
    cur.execute(joint_table_statement)

    for story in stories_dict.keys():
        for sentence_data in stories_dict[story]["story data"]:
            for word in sentence_data[-1]:
                sentence_number = sentence_data[0]
                if word in words_dict.keys():
                    joint_table_tup = (word, word, story, story, story, sentence_number)
                    joint_table_pop_statement = "INSERT INTO '{}' ".format(table_name)
                    joint_table_pop_statement += '''VALUES (
                        (SELECT Id FROM LongestWords WHERE Word = ?), ?,
                        (SELECT Id FROM ShortStories WHERE StoryName = ?), ?,
                        (SELECT Id FROM Sentences WHERE ShortStory = ? AND SentenceInStoryId = ?))
                        '''
                    cur.execute(joint_table_pop_statement, joint_table_tup)
    conn.commit()
    conn.close()
    pass

## Main Program

# Collecting and analyzing data
poe_stories = rerun_or_load("rerun")
common_long_words_dict = find_common_longest_words(poe_stories)

# Function calls to create databases
init_poe_db()
create_short_stories_table(poe_stories)
create_sentences_table(poe_stories)
create_longest_words_table(common_long_words_dict)
create_entries_table(common_long_words_dict)
create_joint_table(poe_stories, common_long_words_dict)
