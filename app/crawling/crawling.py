import csv
import subprocess
from pymongo import MongoClient
import time
import os
from datetime import datetime, timedelta
import schedule

def run_crawling():
    current_date = datetime.now().date()
    yesterday = current_date - timedelta(days=1)

    date_format = yesterday.strftime("%Y-%m-%d")
    filename = 'tweets.csv'
    limit = 50
    
    search_keyword = f'unnes since:{date_format} until:{current_date}'
    
    npx_command = f'npx --yes tweet-harvest@latest -o "{filename}" -s "{search_keyword}" -l {limit} --token "Isi Auth_Token Twitter Anda"'
    result = subprocess.run(npx_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    print("Subprocess Output:", result.stdout)
    print("Subprocess Errors:", result.stderr)
    
    # save_mongo(f"tweets-data/{filename}")
    file_path = os.path.join('tweets-data', 'tweets.csv')
    save_mongo(file_path)


def save_mongo(filepath):
    try:
        # Koneksi ke MongoDB
        with MongoClient('mongodb://localhost:27017/') as client:
            db = client.db_analisis_sentimen
            tweets_collection = db.tweets

            # Membuka file CSV
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for tweet in reader:
                    # Pastikan "id_str" ada dan tidak kosong
                    if tweet.get("id_str") and tweet["id_str"] != "id_str":
                        existing_tweet = tweets_collection.find_one({"full_text": tweet.get("full_text")})

                        if not existing_tweet:
                            tweet_to_save = {
                                "conversation_id_str": tweet.get("conversation_id_str"), 
                                "created_at": tweet.get("created_at"), 
                                "favorite_count": tweet.get("favorite_count"),
                                "full_text": tweet.get("full_text"),
                                "id_str": tweet.get("id_str"),  
                                "username": tweet.get("username"),
                                "tweet_url": tweet.get("tweet_url"),
                                "image_url": tweet.get("image_url"),  
                                "in_reply_to_screen_name": tweet.get("in_reply_to_screen_name"),  
                                "lang": tweet.get("lang"), 
                                "location": tweet.get("location"),  
                                "quote_count": tweet.get("quote_count"),  
                                "reply_count": tweet.get("reply_count"),  
                                "retweet_count": tweet.get("retweet_count"),  
                                "user_id_str": tweet.get("user_id_str"),  
                            }
                            tweets_collection.insert_one(tweet_to_save)

        print("Data berhasil disimpan ke MongoDB.")
    
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def schedule_crawling():
    schedule.every().day.at("13:25").do(run_crawling)
    while True:
        schedule.run_pending()
        time.sleep(10)
        
if __name__ == "__main__":
    # run_crawling()
    schedule_crawling()
