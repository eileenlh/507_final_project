import requests
from bs4 import BeautifulSoup
import time
import json
import csv
import sqlite3 

class Article:
    def __init__(self, date, title, subtitle, author_name, article_url):
        self.date = date
        self.title = title
        self.subtitle = subtitle
        self.author_name = author_name
        self.article_url = article_url

    def get_article_daily(self):
        return f'{self.date}, {self.title}: {self.subtitle}, {self.author_name}, {self.article_url}'

class Author:
    def __init__(self, author_name, author_url, author_bio):
        self.author_name = author_name
        self.author_url = author_url
        self.author_bio = author_bio
    
    def get_author_info(self):
        return f'{self.author_name}, {self.author_url}, {self.author_bio}'

#I didn't eventually use class and instance later in the program. This is only to reflect my initial thinking.

CACHE_FILE_NAME = "cache.json"
CACHE_DICT={}

BASE_URL = 'https://medium.com/tag/covid19/archive/' 

DB_NAME = "covid-19_reader.sqlite"

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache): 
    if (url in cache.keys()): # the url is our unique key
        #print("Using cache") 
        return cache[url]
    else:
        #print("Fetching")
        response = requests.get(url) 
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def get_article_instances_of_the_day(archive):
    '''
    When user enters a date, return all article instances of the day
    '''    
    
    query_url = BASE_URL + archive
    response = make_url_request_using_cache(query_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    #find the url list of all articles of the day
    url_list = []
    article_urls_divs = soup.find_all("div", class_="postArticle-readMore")
    for div in article_urls_divs:
        article_url = div.find("a")["href"]
        #article_id = div.find("a")["data-post-id"]
        url_list.append(article_url)
    
    #author names
    author_name_list = []
    author_name_divs = soup.find_all("div", class_="postMetaInline postMetaInline-authorLockup ui-captionStrong u-flex1 u-noWrapWithEllipsis")
    for div in author_name_divs:
        author_name = div.find("a").text
        author_name_list.append(author_name)
    
    #find all listed article titles and subtitles 
    title_list = []
    subtitle_list = []
    article_listing_divs = soup.find_all("div", class_="section-inner sectionLayout--insetColumn")
    for div in article_listing_divs:
        if div.find("h3") is None:
            title = "No Title"
        else:
            title = div.find("h3").text
        title_list.append(title)

        if div.find("h4") is None:
            subtitle = "No Subtitle"
        else:
            subtitle = div.find("h4").text
        subtitle_list.append(subtitle)

    #get time and date
    date_list = []
    date_tags = soup.find_all("a", class_="link link--darken")
    for tag in date_tags:
        #datetime = tag.find("time")["datetime"]
        date = tag.find("time").text
        date_list.append(date)

    #get author url list
    author_url_list = []
    author_divs = soup.find_all("div", class_="postMetaInline-avatar u-flex0")
    for div in author_divs:
        author_url = div.find("a")["href"]
        author_url_list.append(author_url)
    
    article_of_the_day = zip(date_list, title_list, subtitle_list, author_name_list, url_list)
    article_insts = list(article_of_the_day)
    
    for i in range(len(article_insts)):
        article = article_insts[i]
        print(article) #print out single tuples and will be used as a row

    return article_insts

#then turn the list (article_insts) into a csv files

def make_csv_file(article_insts):
    csvfile = open("articles.csv", "w", newline = "", encoding = "utf-8") 
    writer = csv.writer(csvfile) #check how these two lines work
    writer.writerows(article_insts) 
    #file_reader = csv.reader(csvfile) #IO not readable
    #for row in file_reader:
    #    date = row[0]
    #    title = row[1]
    #    subtitle = row[2]
    #    author = row[3]
    #    url = row[4]
    #    print(date, title, subtitle, author, url)

    csvfile.close()
    return csvfile

def read_csv_file(file_name): #read in the Chinese csv file (only those on a selected date)
    file_to_read = open(file_name,"r") #to make it possible to modify, change the date format to match archive
    file_reader = csv.reader(file_to_read)
    next(file_reader)
    #for row in file_reader:
    #    print(row) #each row is a list
    return file_to_read

#create DB 
#load the Chinese table first

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_cn_sql = '''
        DROP TABLE IF EXISTS "Chinese";
    '''

    create_cn_sql = '''
        CREATE TABLE IF NOT EXISTS "Chinese" (
            "Id"        INTEGER,
            "Category"  TEXT NOT NULL,
            "Update"    TEXT NOT NULL,
            "Media"     TEXT NOT NULL,
            "Date"      TEXT PRIMARY KEY,
            "Title"     TEXT NOT NULL,
            "Title_EN"  TEXT,
            "Translation_EN" TEXT,
            "Is_Deleted" BLOB,
            "Alternative" TEXT,
            "Archive"    TEXT
        );
    '''

    cur.execute(drop_cn_sql)
    cur.execute(create_cn_sql)

    conn.commit()
    conn.close()



if __name__ == "__main__":
    #while true
    CACHE_DICT = load_cache()
    archive = input("Please enter a date (format yyyy/mm/dd), beginning with 2020/01/20: ")
    article_insts = get_article_instances_of_the_day(archive)
    temp_file = make_csv_file(article_insts) 
    cn_file = read_csv_file("data.csv")
    create_db()
    


    
    



