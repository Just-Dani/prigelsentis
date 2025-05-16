import flask
from flask import Flask
import threading
from app.helpers import schedule_sentimen
from app.crawling.crawling import schedule_crawling as twitter_schedule_crawling
from app.crawling.instagram_scrapper import schedule_crawling as instagram_schedule_crawling
from app.crawling.alin import schedule_crawling as facebook_schedule_crawling
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client.db_analisis_sentimen
tweets_collection = db.tweets
insta_collection = db.instagram
facebook_collection = db.facebook

# for document in insta_collection.find():
#     print(document)

if __name__ == '__main__':

    twitter_crawling_thread = threading.Thread(target=twitter_schedule_crawling)
    twitter_crawling_thread.start()
    
    instagram_crawling_thread = threading.Thread(target=instagram_schedule_crawling)
    instagram_crawling_thread.start()

    facebook_crawling_thread = threading.Thread(target=facebook_schedule_crawling)
    facebook_crawling_thread.start()
    
    sentiment_thread = threading.Thread(target=schedule_sentimen, args=(tweets_collection, insta_collection, facebook_collection, False))
    sentiment_thread.start()
    
    from app.routes import app as routes_app
    routes_app.run(debug=True)