import unittest
from final_project import *
from final_project_interactive import *

class TestDataCollection(unittest.TestCase):

    def test_wikisource_scraping(self):
        morella_text = join_paragraphs(extract_poe_story("/wiki/Morella_(1835)"))
        self.assertEqual(type(morella_text), type("string"))
        self.assertTrue("MORELLA" not in morella_text)
        self.assertTrue("public domain" not in morella_text)

    def test_merriam_webster_call(self):
        data = gather_dictionary_data_for_word("despicable")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][1], "adjective")
        self.assertEqual(data[0][3], "1553")

class TestDataStorage(unittest.TestCase):

    def test_sentence_processing(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        test_sentence_statement = '''SELECT * FROM Sentences WHERE ShortStory = "The Murders in the Rue Morgue"'''
        cur.execute(test_sentence_statement)
        third_to_last_tup = cur.fetchall()[-3]
        conn.close()
        self.assertEqual(third_to_last_tup[4], "I like him especially for one master stroke of cant, by which he has attained his reputation for ingenuity.")
        self.assertEqual(third_to_last_tup[6], ".")
        self.assertEqual(third_to_last_tup[7], 19)
        self.assertEqual(third_to_last_tup[9], "especially, reputation")

    def test_entry_processing(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        test_entry_statement = '''SELECT * FROM Entries WHERE Word = "disappeared"'''
        cur.execute(test_entry_statement)
        disappear_entry = cur.fetchall()
        conn.close()
        self.assertEqual(len(disappear_entry), 1)
        self.assertEqual(disappear_entry[0][2], "disappear")
        self.assertTrue("2)" in disappear_entry[0][4])

class TestDataProcessing(unittest.TestCase):

    def test_story_class(self):
        usher = Story("The Fall of the House of Usher")
        self.assertEqual(usher.median_sent_length, 23)
        self.assertEqual(usher.year, 1846)
        self.assertEqual(len(usher.sentence_lengths), 241)

    def test_word_class(self):
        arrangements = Word("arrangements")
        self.assertEqual(arrangements.__str__(), "arrangements: times longest: 17; dictionary entries: 1")
        self.assertEqual(arrangements.collect_longest_word_appearances().count(", sentence"), 17)

unittest.main()
