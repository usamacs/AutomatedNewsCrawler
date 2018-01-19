# AutomatedNewsCrawler
This Project uses news-please with little updation and boilerpipe to crawl news and generate XML files of it. It get the news content and automatically classify it by machine learning into the different categories

Now we can crawl Urdu News websites too.!

In this project we only provide Base URLS of News Websites in configuration file located under config/ directory
This project picks up each URL one by one and crawl all new news from that news website with time limit. 
i have provided time limit of 2 Days in configuration file. which means it will only crawl those news which are posted with in last 48 hours.
it will leave news which are older then our time limit.

It will Get News 
1- Posted Time (by News-Please, I have updated date_extractor class of this library to work for our case. Urdu Sites etc.)  
2- News Image (by News-Please)  
3- Title (by News-Please)  
4- Content (by Boilerpipe)  
5- group of the news wether it is of science category or health category, international or national. classification is done by machine learning algorithem.  

we then download image and put it into a directory provided in configuration file in conf/ directory
and put generated XML file into XML directory provided into configuration file in conf/ directory
