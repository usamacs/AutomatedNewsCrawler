

class Article:
    def __init__(self):
        self.title = None
        self.content = None
        self.published_date = None
        self.tag = None
        self.group = None
        self.url = None
        self.img_url = None
        self.adpath = None

    def set_title(self, title):
        self.title = title

    def set_content(self, content):
        self.content = content

    def set_published_date(self, pubDate):
        self.published_date = pubDate

    def set_tag(self, tag):
        self.tag = tag

    def set_group(self, group):
        self.group = group

    def set_url(self, url):
        self.url = url

    def set_img_url(self, img_url):
        self.img_url = img_url

    def set_adpath(self, adpath):
        self.adpath = adpath

    def get_title(self):
        return self.title

    def get_content(self):
        return self.content

    def get_published_date(self):
        return self.published_date

    def get_tag(self):
        return self.tag

    def get_group(self):
        return self.group

    def get_url(self):
        return self.url

    def get_img_url(self):
        return self.img_url

    def get_adpath(self):
        return self.adpath