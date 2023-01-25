# chromium

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re
import sqlite3
from sqlite3 import Error
import types
import pandas as pd


class QuoteMaster(object):
    def __init__(self):
        self.create_connection(r"mydb.db")
        self.open_conn()
        self.scrape_data()
        self.close_commit()

    def scrape_data(self):
        options = Options()
        options.add_argument("--headless")

        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        PATH = r"./chrome_driver/chromedriver_mac64"

        pattern = '\A.*'

        # url we want to scrape data from
        url = 'http://www.quotationspage.com/random.php'

        # open url in browser
        driver.get(url)

        quote_class = 'quote'
        author_class = 'author'

        quotes = driver.find_elements(By.CLASS_NAME, quote_class)
        authors = driver.find_elements(By.CLASS_NAME, author_class)

        record = types.SimpleNamespace()

        index = 1
        for quote, author in zip(quotes, authors):
            quote_clean = quote.get_attribute("innerText")
            # print(quote_clean)
            author_str = author.get_attribute("innerText")
            author_clean = re.match(pattern, author_str).group()
            # print('****' + author_clean)
            # print('\n')
            record.id = index
            record.quote = quote_clean
            record.author = author_clean
            self.insert_record(record=record)
            index = index + 1

    def open_conn(self):
        self.conn = sqlite3.connect('mydb.db')
        self.curser = self.conn.cursor()

    def close_commit(self):
        self.conn.commit()
        self.conn.close()

    def insert_record(self, record):
        self.curser.execute('INSERT INTO quotes (quote_id, quote_text, quote_author) '
                            'VALUES(?,?,?)', (record.id, record.quote, record.author))

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)

            c = conn.cursor()

            c.execute('''
            CREATE TABLE IF NOT EXISTS quotes
            ([quote_id] INTEGER PRIMARY KEY, [quote_text] TEXT, [quote_author] TEXT)
            ''')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def fetch_from_db(self):
        conn = sqlite3.connect('mydb.db')
        c = conn.cursor()

        c.execute('''
                SELECT
                quote_id,
                quote_text,
                quote_author
                FROM quotes 
                ''')

        df = pd.DataFrame(c.fetchall(), columns=['id', 'quote', 'author'])
        print(df)
        conn.close()


if __name__ == '__main__':
    q = QuoteMaster()
    q.fetch_from_db()
