import flask
from flask import Flask
import threading
from app.helpers import schedule_sentimen
from app.crawling.crawling import schedule_crawling as twitter_schedule_crawling
from app.crawling.instagram_scrapper import schedule_crawling as instagram_schedule_crawling
from app.crawling.facebook_scrapper import schedule_crawling as facebook_schedule_crawling
# Import scrapper TikTok dan YouTube jika ada di crawling module
# Pastikan modul ini ada dan berisi fungsi schedule_crawling
try:
    from app.crawling.tiktok_comment_scrapper import schedule_crawling as tiktok_schedule_crawling
except ImportError:
    tiktok_schedule_crawling = None
    print("Peringatan: Modul tiktok_comment_scrapper tidak ditemukan. Crawling TikTok mungkin tidak berfungsi.")
try:
    from app.crawling.youtube_comment_scrapper import schedule_crawling as youtube_schedule_crawling
except ImportError:
    youtube_schedule_crawling = None
    print("Peringatan: Modul youtube_comment_scrapper tidak ditemukan. Crawling YouTube mungkin tidak berfungsi.")

from pymongo import MongoClient
# Mengimpor aplikasi Flask dari app/__init__.py
from app import create_app

# Membuat instance aplikasi Flask
app = create_app()

# Menginisialisasi koneksi MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.db_analisis_sentimen
tweets_collection = db.tweets
insta_collection = db.instagram
facebook_collection = db.facebook
# Menambahkan koleksi TikTok dan YouTube
tiktok_collection = db.tiktok
youtube_collection = db.youtube

if __name__ == '__main__':
    # Anda dapat mengaktifkan thread crawling jika diperlukan
    # if twitter_schedule_crawling:
    #     twitter_crawling_thread = threading.Thread(target=twitter_schedule_crawling)
    #     twitter_crawling_thread.start()
    
    # if instagram_crawling_thread:
    #     instagram_crawling_thread = threading.Thread(target=instagram_schedule_crawling)
    #     instagram_crawling_thread.start()

    # if facebook_schedule_crawling:
    #     facebook_crawling_thread = threading.Thread(target=facebook_schedule_crawling)
    #     facebook_crawling_thread.start()

    # Mengaktifkan thread crawling TikTok dan YouTube
    # Pastikan fungsi schedule_crawling di tiktok_comment_scrapper dan youtube_comment_scrapper ada
    # if tiktok_schedule_crawling:
    #     tiktok_crawling_thread = threading.Thread(target=tiktok_schedule_crawling)
    #     tiktok_crawling_thread.start()

    # if youtube_schedule_crawling:
    #     youtube_crawling_thread = threading.Thread(target=youtube_schedule_crawling)
    #     youtube_crawling_thread.start()
    
    # Memulai thread untuk analisis sentimen
    # Memperbarui argumen untuk schedule_sentimen agar menyertakan koleksi TikTok dan YouTube
    sentiment_thread = threading.Thread(target=schedule_sentimen, args=(tweets_collection, insta_collection, facebook_collection, tiktok_collection, youtube_collection, False))
    sentiment_thread.start()
    
    # Menjalankan aplikasi Flask
    app.run(debug=True)

