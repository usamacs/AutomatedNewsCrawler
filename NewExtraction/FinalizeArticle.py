#! /usr/bin/env python
#! -*- coding: utf-8 -*-
import os, time, hashlib
from NewExtraction.xml_formatter import Generate_XML

class FinalizeArticle:

    def __init__(self, retry_limit):
        self.img_server_path = None
        self.domain_path = None
        self.RETRY_LIMIT = retry_limit

    def DownloadAndStoreImage(self, image_url, news_url, IMAGE_DIR, IMAGE_THUMBNAIL_DIR, SOURCE, image_tolerance):
        # Image Name
        img_name = self.createMD5hash(image_url)
        img_extension = image_url.split('.')[-1].split('?')[0]
        img_name = img_name + "." + img_extension
        #img_name = img_name.split('?')[0]
        #date_info = time.time()
        #img_name = str(date_info).split(".")[0] + "_" + img_name

        # Current month
        current_month = time.strftime('%Y_%b')
        self.domain_path = SOURCE + "/" + current_month
        image_store_path = IMAGE_DIR + self.domain_path
        # Fetch image in respective folder
        state = self.fetchImage(image_url, image_store_path, img_name)
        if state == False and image_tolerance == "False":
            print("Image Not avaialbe: skipping ", news_url)
            return "Error"

        self.img_server_path = IMAGE_THUMBNAIL_DIR + self.domain_path + "/" + img_name
        return self.img_server_path


    def fetchImage(self, image_url, dst, img_name):
        _error = True
        counter = 0
        try:
            if not os.path.isdir(dst):
                print("WARN:Creating directory : %s" % (dst))
                os.makedirs(dst)
        except Exception as e:
            print(e)

        while _error and counter < self.RETRY_LIMIT:
            try:
                command = "wget %s -O %s" % (image_url, dst + '/' + img_name)
                os.system(command)
                _error = False
            except Exception as err:
                counter = counter + 1
                _error = True
                print("ImageFetchError: %s\t%s" % (image_url, err))

        if _error:
            return False
        else:
            return True

    def createMD5hash(self, url):
        url = url.encode("utf-8")
        hash_object = hashlib.md5(url)
        unique_key = hash_object.hexdigest()
        return unique_key

    def generate_xml_directory(self, xml_path):
        try:
            if not os.path.isdir(xml_path):
                print("WARN:Creating directory : %s" % (xml_path))
                os.makedirs(xml_path)
                return True
            else:
                print("Already a Directory")
                return True
        except Exception as e:
            print(e)
            return False

    def Generate_XML_FILE(self, XML_DIR, SOURCE, article):
        xml_path = XML_DIR + SOURCE
        if self.generate_xml_directory(xml_path):
            Generate_XML(article.get_title(), article.get_url(), article.get_group(), article.get_adpath(), outDir= xml_path,
                                 text= article.get_content(), date=article.get_published_date(), tag= article.get_tag())