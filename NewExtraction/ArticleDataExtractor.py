from newsplease import NewsPlease

class ArticleDataExtractor:
    def __init__(self, retry_limit):
        self.article_date = None
        self.article_image = None
        self.article_title = None
        self.Retry_Limit = retry_limit

    def news_article_date_extractor(self, url):
        error = True
        counter = 0
        while error and counter < self.Retry_Limit:
            try:
                article = NewsPlease.from_url(url)
                self.article_date = article.date_publish
                self.article_image = article.image_url
                self.article_title = article.title
                error = False
            except Exception as e:
                counter = counter + 1
                self.article_date = None
                print(e)
                print(url + " ---> Retrying...")
                error = True


        return self.article_date

    def get_article_image(self):
        return self.article_image

    def get_article_title(self):
        return self.article_title