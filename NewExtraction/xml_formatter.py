#! /usr/bin/env python
# ! -*- coding: utf-8 -*-
import re
import hashlib


# this method removes special character (solr) in text
def remove_special_chars(txt):
    stopWords = r'[,&#\'":`]'
    # txt=txt.encode('utf-8')
    updated_text = re.sub(stopWords, " ", txt)
    return updated_text

def createMD5hash(url):
    url = url.encode("utf-8")
    hash_object = hashlib.md5(url)
    unique_key = hash_object.hexdigest()
    return unique_key

def Generate_XML(title, url, group, img_path, typ="", id_="", outDir="",
                 author="", file_name="", date="", text="", tag="", URDU_PARSER=False):
    # URDU_PARSER: if it is set true, then it will remove all characters
    #  other than URDU unicode range. for example all English is removed
    # img_path: path relative to webserver like _i/news/dawn/2017_Sep/image.jpg
    out_file = ""
    if id_ == "":
        out_file = createMD5hash(url)
        tok = url.split("/")
        host = tok[2]
        part = host.split('.')
        count = 1
        id_ = part[len(part) - 1]
        for item in part:
            if count == 1:
                count = count + 1
                continue
            id_ = id_ + '.' + part[len(part) - count]
            count = count + 1
        tmp1 = tok[0].split(':')
        protocol = ':' + tmp1[0]
        id_ = id_ + protocol + '/' + '/'.join(map(str, tok[3:]))
        # Output file creation
        out_file = outDir + '/' + out_file + '.xml'
    output_f = open(out_file, 'w')

    title_parsed = remove_special_chars(title)
    if URDU_PARSER == True:
        title_parsed = PARSE_URDU_TEXT(title_parsed)
        text = PARSE_URDU_TEXT(text)

    output_f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>'+"\n")
    output_f.write('<add><doc>'+"\n")
    output_f.write('<field name="id">' + id_ + "</field>"+"\n")
    output_f.write('<field name="title">' + title_parsed + "</field>" + "\n")
    #print >> output_f, '<add><doc>'
    #print >> output_f, '<field name="id">' + id_ + "</field>"
    #print >> output_f, '<field name="title">' + title_parsed + "</field>"
    if date != "":
        output_f.write('<field name="date">' + date + '</field>' + "\n")
        #print >> output_f, '<field name="date">' + date + '</field>'
    if text != "":
        content_parsed = remove_special_chars(text)
        output_f.write('<field name="content">' + content_parsed + "</field>" + "\n")
        #print >> output_f, '<field name="content">' + content_parsed + "</field>"
    if tag != "":
        output_f.write('<field name="tag">' + tag + '</field>' + "\n")
        #print >> output_f, '<field name="tag">' + tag + '</field>'

    output_f.write('<field name="group">' + group + '</field>' + "\n")
    output_f.write('<field name="adpath">' + img_path + '</field>' + "\n")
    output_f.write('<field name="url">' + url + '</field>' + "\n")
    output_f.write("</doc></add>" + "\n")
    #print >> output_f, '<field name="group">' + group + '</field>'
    #print >> output_f, '<field name="adpath">' + img_path + '</field>'
    #print >> output_f, '<field name="url">' + url.encode('utf-8') + '</field>'
    #print >> output_f, "</doc></add>"


# This method removes all non urdu characters except numbers
# It only checks first character of each word
# If urdu then it is assumed that complete word is urdu
def PARSE_URDU_TEXT(s):
    parsed_text = []  # List to store final values
    s = s.decode('utf8')
    str_array = s.split(" ")
    for word in str_array:
        word = word.strip()
        if len(word) == 0:
            continue
        unicode_vale = ord(word[0])
        # Allow Urdu unicode only x0600 to x06FF
        if unicode_vale >= 1536 and unicode_vale <= 1791 or unicode_vale >= 48 and unicode_vale <= 57:
            parsed_text.append(word)

            # Return parsed text
    return ' '.join(parsed_text).encode('utf8')
