from boilerpipe.extract import Extractor

class ArticleTextExtractor:
    def __init__(self, retry_limit):
        self.article_text = None
        self.Retry_Limit = retry_limit

    def news_article_text_extractor(self, url):
        error = True
        counter = 0
        while error and counter < self.Retry_Limit:
            try:
                extractor = Extractor(extractor='ArticleExtractor', url=url)
                self.article_text = extractor.getText().split("\n")
                self.article_text = " ".join(self.article_text)
                error = False
            except Exception as e:
                counter = counter + 1
                self.article_text = None
                print(e)
                print(" ---> Retrying...")
                error = True


        return self.article_text