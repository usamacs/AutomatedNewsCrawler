#! /usr/bin/python

import configparser, threading

import os
import simplejson as simplejson
from bs4 import BeautifulSoup
import re, requests
import logging
from datetime import datetime
import time
import urllib.request, json


from NewExtraction.ArticleDataExtractor import ArticleDataExtractor
from NewExtraction.Article import Article
from NewExtraction.ArticleTextExtractor import ArticleTextExtractor
from NewExtraction.NewsClassifier import NewsClassifier
from NewExtraction.FinalizeArticle import FinalizeArticle


class NewsSources:
    parser = configparser.ConfigParser()
    parser.read("../config/configuration.ini")

    def __init__(self):
        self.URLs_dict = self.confParser( "news_sources" )
        self.conf_dict = self.confParser( "general" )
        self.urdu_names_dict = self.confParser("source_urdu_names")
        self.Solr_info = self.confParser("solr_info")


    def confParser(self, section):

        if not self.parser.has_section(section):
            print("No section information are available in config file for", section)
            return
        # Build dict
        tmp_dict = {}
        for option, value in self.parser.items(section):
            option = str(option)
            value = value
            tmp_dict[option] = value
        return tmp_dict

    def get(self, src):
        if src == "url":
            return self.URLs_dict
        elif src == "general":
            return self.conf_dict
        elif src == "ur_names":
            return self.urdu_names_dict
        elif src == "solr_info":
            return self.Solr_info


            # Main governing function

    def fetchCategoryURLs(self, src_url, src_url_base):
        #  category_url = bbc.com/natioonal-14334
        # src_url = bbc.com
        try:
            r = requests.get(src_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            r.encoding = "utf-8"
            page = r.text
        except:
            print("%s URL not accessible " % (src_url))
            #general_logger.warn("LINKDOWN: %s " % (url_page))
            return

        page_obj = BeautifulSoup(page, "lxml")
        urls_list = page_obj.findAll('a')
        out_url_list = []

        last_url = None
        last_link = None
        for url in urls_list:
            try:
                news_url = url['href']
            except Exception:
                print("href not found in ", url)

            # print news_url
            news_url = news_url.strip().split("#")[0]
            # handle bbc case
            if src == "bbc":
                news_url = "http://www.bbc.com" + news_url

            len_news_url = len(news_url)
            len_src_url = len(src_url)
            news_url = str(news_url)
            src_url = str(src_url)

            if news_url.startswith(src_url) and len_news_url > len_src_url and last_url != news_url:
                # page Level Analysis
                last_url = news_url
                splitted_url = news_url.split("/")
                for s in splitted_url:
                    if s == "":
                        splitted_url.remove(s)
                # print last_url
                if last_url not in out_url_list:
                    out_url_list.append(last_url)

            elif news_url.startswith("/") and src_url_base + news_url != last_link:
                last_link = src_url_base + news_url
                if last_link not in out_url_list:
                    out_url_list.append(last_link)

        # Return List of URLs
        return out_url_list

    def isDuplicateUrl(self, page_url):
        file = open(URL_LOGS,"r")
        line = file.readline().split("\n")[0]
        while line != "":
            if line == page_url:
                return True
            line = file.readline().split("\n")[0]

        file.close()

        file = open(SKIPPED_URLS_LOGS, "r")
        line = file.readline().split("\n")[0]
        while line != "":
            if line == page_url:
                return True
            line = file.readline().split("\n")[0]

        file.close()

        return False


def Write_URL_TO_FILE(URL_LOGS, url_v):
    fo = open(URL_LOGS, "a")
    fo.write(url_v+"\n")
    fo.close()

def Clear_File(File_Name):
    open(File_Name, 'w').close()

def toTimeStamp(date):
    return time.mktime(date.timetuple())

def passDateFilter(date):
    current_timestamp = time.time()
    current_timestamp = int(str(current_timestamp).split(".")[0])
    article_timestamp = toTimeStamp(datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ"))
    difference = current_timestamp - article_timestamp
    difference = int(str(difference).split(".")[0])
    difference_in_hours = int(((difference /60) / 60))
    hours_limit = ARTICLE_DAYS_LIMIT * 24
    if difference_in_hours <= hours_limit:
        return True
    else:
        return False

def ExtractArticleData(article_data_extractor, article_text_extractor, article_date, url, news_classifier, img_tolerance, src):
    article_obj = Article()
    article_obj.set_title(article_data_extractor.get_article_title())
    article_obj.set_published_date(article_date)
    article_obj.set_img_url(article_data_extractor.get_article_image())
    article_obj.set_content(article_text_extractor.news_article_text_extractor(url))
    if article_obj.get_content() == None or article_obj.get_content() == "" :
        print("Article Text Not Found...> Skipping ---> " + url)
        article_obj = None
    else:
        article_obj.set_group(news_classifier.Predict_Group(article_obj.get_content()))
        article_obj.set_url(url)
        article_obj.set_tag(src)
        if article_obj.get_img_url() == None or article_obj.get_img_url() == "" and img_tolerance == False:
            article_obj = None
    return article_obj

def Download_News_Article(article_data_extractor, article_text_extractor, article_date, url, news_classifier, src_ur_name, src):
    article = ExtractArticleData(article_data_extractor, article_text_extractor,
                                 article_date,
                                 url, news_classifier, IMAGE_TOLERANCE,
                                 src_ur_name)
    if article != None:
        result = finalize_article.DownloadAndStoreImage(article.get_img_url(),
                                                        article.get_url(),
                                                        IMAGE_DIR, IMAGE_THUMBNAIL_DIR, src,
                                                        IMAGE_TOLERANCE)
        if result != "Error":
            article.set_adpath(result)
            finalize_article.Generate_XML_FILE(XML_DIR, src, article)
            print("Category " + article.get_group())
            print("Successfully Generated XML for ---> " + url)
        else:
            print("Image Download Failed...Skipping ---> " + article.get_img_url())
            article = None
    return article

def CheckExistanceImSolr(url, retry_limit):
    count = 0
    numFound = None
    query = "http://" + solr_info["ip"] + ":" + solr_info["port"] + "/solr/" + solr_info["core"] + "/" + "select?df=url&indent=on&q=" + "\""+ url + "\"&wt=json"
    while numFound == None and count < retry_limit:
        try:
            with urllib.request.urlopen(query) as url_response:
                data = json.loads(url_response.read().decode())
                numFound = data["response"]["numFound"]
        except:
            count = count + 1
            numFound = None
            print("Solr Issue for ---> " + url)

    return numFound

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError

def create_files_if_not_exist():
    temp = URL_LOGS.split('/')
    del temp[-1]
    _dir = ""
    for s in temp:
        _dir = _dir + s + "/"

    if not os.path.exists(_dir):
        os.makedirs(_dir)
    if not os.path.exists(URL_LOGS):
        file = open(URL_LOGS, "w")
        file.close()
    if not os.path.exists(APP_LOGS):
        file = open(APP_LOGS, "w")
        file.close()
    if not os.path.exists(ALREADY_INDEXED_LOGS):
        file = open(ALREADY_INDEXED_LOGS, "w")
        file.close()
    if not os.path.exists(SKIPPED_URLS_LOGS):
        file = open(SKIPPED_URLS_LOGS, "w")
        file.close()

if __name__ == '__main__':
    start_time  = time.time()
    URL_LOGS = "../logs/processed_urls.log"
    APP_LOGS = "../logs/logfile.log"
    ALREADY_INDEXED_LOGS = "../logs/already_indexed.log"
    SKIPPED_URLS_LOGS = "../logs/skipped_urls.log"
    obj = NewsSources()
    urls = obj.get("url")
    general_conf = obj.get( "general" )
    urdu_names = obj.get( "ur_names" )
    solr_info = obj.get("solr_info")

    create_files_if_not_exist()

    ARTICLE_DAYS_LIMIT = int(general_conf["article_days_limit"])
    IMAGE_TOLERANCE = str_to_bool(general_conf["image_tolerance"])
    IMAGE_THUMBNAIL_DIR = general_conf["srv_thumbnail_dir"]
    IMAGE_DIR = general_conf["image_dir"]
    XML_DIR = general_conf["xml_dir"]
    RETRY_LIMIT = int(general_conf["retry_limit"])
    logging.basicConfig(filename=APP_LOGS, level=logging.INFO)

# Objects
    article_data_extractor = ArticleDataExtractor(RETRY_LIMIT)
    article_text_extractor = ArticleTextExtractor(RETRY_LIMIT)
    news_classifier = NewsClassifier()
    finalize_article = FinalizeArticle(RETRY_LIMIT)


    if ARTICLE_DAYS_LIMIT == None:
        ARTICLE_DAYS_LIMIT = 2
    if IMAGE_TOLERANCE == None:
        IMAGE_TOLERANCE = False

    for src in urls:
        print("Starting "+src + " Category...")
        out_links_urls = []
        src_ur_name = urdu_names[src]
        src_url = urls[src]
        tmp_url_split = src_url.split("|")
        src_url_base = tmp_url_split[0]
        src_url = tmp_url_split[0]+tmp_url_split[-1]
        article = Article()
        #category_limit_check = category_limit_rule.fromkeys( category_limit_rule.iterkeys(), 0)
        article_urls = obj.fetchCategoryURLs(src_url, src_url_base)
        while article_urls == None:
            article_urls = obj.fetchCategoryURLs(src_url, src_url_base)

        _quit = False
        counter = 0

        while len(article_urls) > 0 and not _quit :
            if not obj.isDuplicateUrl(article_urls[0]):
                numFound = CheckExistanceImSolr(article_urls[0], RETRY_LIMIT)
                if numFound != None and numFound == 0:
                    article_date = article_data_extractor.news_article_date_extractor(article_urls[0])
                    if article_date != None:
                        article_date = datetime.strptime(str(article_date), '%Y-%m-%d %H:%M:%S')
                        article_date = datetime.strftime(article_date, '%Y-%m-%dT%H:%M:%SZ')
                        #logging.debug(article_urls[0])
                        Write_URL_TO_FILE(URL_LOGS,article_urls[0])
                        if passDateFilter(article_date):
                            print("News Ok")
                            if counter < 20:
                                counter = counter + 1
                            Download_News_Article(article_data_extractor, article_text_extractor, article_date,
                                                  article_urls[0], news_classifier, src_ur_name, src)
                            if counter >= 20:
                                _quit = False#True
                        else:
                            print(article_urls[0] + " ---> News is Older than our time limit...")
                        article_urls.pop(0)
                    else:
                        print(article_urls[0] + " ---> Adding in list for further url fetching...")
                        out_links_urls.append(article_urls[0])
                        article_urls.pop(0)
                else:
                    print(article_urls[0] + " ---> Already Indexed in Solr")
                    Write_URL_TO_FILE(ALREADY_INDEXED_LOGS, article_urls[0])
                    article_urls.pop(0)
            else:
                print("Duplicate URL")
                article_urls.pop(0)

        while len(out_links_urls) > 0 and not _quit:
            if not obj.isDuplicateUrl(out_links_urls[0]):
                article_urls = obj.fetchCategoryURLs(out_links_urls[0], src_url_base)
                while article_urls == None:
                    article_urls = obj.fetchCategoryURLs(out_links_urls[0], src_url_base)

                while len(article_urls) > 0:
                    if not obj.isDuplicateUrl(article_urls[0]):
                        article_date = article_data_extractor.news_article_date_extractor(article_urls[0])
                        if article_date != None:
                            numFound = CheckExistanceImSolr(article_urls[0], RETRY_LIMIT)
                            if numFound != None and numFound == 0:
                                article_date = datetime.strptime(str(article_date), '%Y-%m-%d %H:%M:%S')
                                article_date = datetime.strftime(article_date, '%Y-%m-%dT%H:%M:%SZ')
                                Write_URL_TO_FILE(URL_LOGS, article_urls[0])
                                if passDateFilter(article_date):
                                    print("News OK")
                                    if counter < 20:
                                        counter = counter + 1
                                    Download_News_Article(article_data_extractor, article_text_extractor, article_date, article_urls[0], news_classifier, src_ur_name, src)
                                    if counter >= 20:
                                        _quit = False#True
                                else:
                                    print(article_urls[0] + " ---> News is Older than our time limit...")
                            else:
                                print(article_urls[0] + " ---> Already Indexed in Solr")
                                Write_URL_TO_FILE(ALREADY_INDEXED_LOGS, article_urls[0])
                            article_urls.pop(0)
                        else:
                            Write_URL_TO_FILE(SKIPPED_URLS_LOGS , article_urls[0])
                            print(article_urls[0] + " ---> IGNORING...")
                            article_urls.pop(0)
                    else:
                        print("Already Processed")
                        article_urls.pop(0)

                #logging.debug(out_links_urls[0])
                Write_URL_TO_FILE(URL_LOGS, out_links_urls[0])
                out_links_urls.pop(0)
            else:
                print("Duplicate URL")
                out_links_urls.pop(0)


    Clear_File(URL_LOGS)
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution Time in Seconds = " + str(execution_time))