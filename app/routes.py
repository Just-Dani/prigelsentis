import pymongo
from flask import Flask, request, jsonify, render_template, redirect, url_for, get_flashed_messages, flash
from pymongo import MongoClient
from bson import json_util
from flask_bcrypt import Bcrypt
import secrets
from .helpers import tabel_sentimen
from app import app
from bson import ObjectId


app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client.db_analisis_sentimen
users_collection = db.users
tweets_collection = db.tweets
instagram_collection = db.instagram
facebook_collection = db.facebook

bcrypt = Bcrypt(app) 
app.secret_key = secrets.token_hex(16)

@app.route('/delete_tweet_data/<string:id>', methods=['DELETE'])
def delete_tweet_data(id):
    result = tweets_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404


@app.route('/delete_instagram_data/<string:id>', methods=['DELETE'])
def delete_instagram_data(id):
    result = instagram_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

@app.route('/delete_facebook_data/<string:id>', methods=['DELETE'])
def delete_facebook_data(id):
    result = facebook_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

@app.route("/", methods=['GET'])
def index():
    return render_template('login.html')
    # return 'Hello, World!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = users_collection.find_one({'username': username})

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'username': username, 'password': hashed_password})

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password'], password):
            return redirect(url_for('dashboard'))
        else:
            # Flash pesan error jika login gagal
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index-twit.html')

@app.route('/instagram')
def instagram():
    return render_template('index-insta.html')

@app.route('/facebook')
def facebook():
    return render_template('index-face.html')

@app.route('/instagram-positif')
def instagram_positif():
    return render_template('positif-insta.html')

@app.route('/instagram-negatif')
def instagram_negatif():
    return render_template('negatif-insta.html')

@app.route('/instagram-netral')
def instagram_netral():
    return render_template('netral-insta.html')

@app.route('/twitter-positif')
def twitter_positif():
    return render_template('positif-tweet.html')

@app.route('/twitter-negatif')
def twitter_negatif():
    return render_template('negatif-tweet.html')

@app.route('/twitter-netral')
def twitter_netral():
    return render_template('netral-tweet.html')

@app.route('/facebook-positif')
def facebook_positif():
    return render_template('positif-face.html')

@app.route('/facebook-negatif')
def facebook_negatif():
    return render_template('negatif-face.html')

@app.route('/facebook-netral')
def facebook_netral():
    return render_template('netral-face.html')

@app.route('/data', methods=['GET'])
def get_data():
    tweets_data = list(tweets_collection.find({}, {'_id': 1, 'created_at': 1, 'full_text': 1, 'sentimen': 1, 'grade': 1, 'tweet_url': 1}))
    formatted_data = []
    for tweet in tweets_data:
        formatted_tweet = {
            '_id': str(tweet['_id']),
            'created_at': tweet.get('created_at', ''),
            'full_text': tweet.get('full_text', ''),
            'sentimen': tweet.get('sentimen', ''),
            'grade': tweet.get('grade', ''),  # tambahkan 'grade' di sini
            'tweet_url': tweet.get('tweet_url', '')
        }
        formatted_data.append(formatted_tweet)

    return jsonify({'status': 'success', 'result_data': formatted_data})



@app.route('/search_tweets', methods=['GET'])
def search_tweets():
    search_query = request.args.get('q', '').lower()
    matched_tweets = list(tweets_collection.find({'full_text': {'$regex': search_query}}, {'_id': 1, 'created_at': 1, 'full_text': 1, 'sentimen': 1, 'tweet_url': 1, 'grade': 1}))
    formatted_data = []
    for tweet in matched_tweets:
        formatted_tweet = {
            '_id': str(tweet['_id']),
            'created_at': tweet.get('created_at', ''),
            'full_text': tweet.get('full_text', ''),
            'sentimen': tweet.get('sentimen', ''),
            'grade': tweet.get('grade', ''),  # tambahkan 'grade' di sini
            'tweet_url': tweet.get('tweet_url', '')
        }
        formatted_data.append(formatted_tweet)

    return jsonify({'status': 'success', 'result_data': formatted_data})

@app.route('/instagram_data', methods=['GET'])
def get_instagram_data():
    instagram_data = list(instagram_collection.find({}, {'_id': 1, 'URL': 1, 'Username': 1, 'Comment': 1, 'Date': 1, 'sentimen': 1, 'grade': 1}))  # tambahkan 'grade': 1 di sini
    formatted_data = []
    for post in instagram_data:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Date', ''),
            'URL': post.get('URL', ''),
            'Username': post.get('Username', ''),
            'Comment': post.get('Comment', ''),
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')  # tambahkan 'grade' di sini
        }
        formatted_data.append(formatted_post)
    return jsonify({'status': 'success', 'result_data': formatted_data})

@app.route('/search_instagram', methods=['GET'])
def search_instagram():
    search_query = request.args.get('q', '').lower()
    matched_posts = list(instagram_collection.find({'$or': [
        {'Username': {'$regex': search_query, '$options': 'i'}},
        {'Comment': {'$regex': search_query, '$options': 'i'}}
    ]}, {'_id': 1, 'URL': 1, 'Username': 1, 'Comment': 1, 'Date': 1, 'sentimen': 1, 'grade': 1}))  # tambahkan 'grade': 1 di sini
    formatted_data = []
    for post in matched_posts:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Date', ''),
            'URL': post.get('URL', ''),
            'Username': post.get('Username', ''),
            'Comment': post.get('Comment', ''),
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')  # tambahkan 'grade' di sini
        }
        formatted_data.append(formatted_post)
    return jsonify({'status': 'success', 'result_data': formatted_data})

@app.route('/facebook_data', methods=['GET'])
def get_facebook_data():
    facebook_data = list(facebook_collection.find({}, {
        '_id': 1,
        'URL': 1,
        'Username': 1,
        'Comment': 1,
        'Date': 1,
        'sentimen': 1,
        'grade': 1  # include grade
    }))
    
    formatted_data = []
    for post in facebook_data:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Date', ''),
            'URL': post.get('URL', ''),
            'Username': post.get('Username', ''),
            'Comment': post.get('Comment', ''),
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)

    return jsonify({'status': 'success', 'result_data': formatted_data})

@app.route('/search_facebook', methods=['GET'])
def search_facebook():
    search_query = request.args.get('q', '').lower()
    matched_posts = list(facebook_collection.find({'$or': [
        {'Username': {'$regex': search_query, '$options': 'i'}},
        {'Comment': {'$regex': search_query, '$options': 'i'}}
    ]}, {
        '_id': 1,
        'URL': 1,
        'Username': 1,
        'Comment': 1,
        'Date': 1,
        'sentimen': 1,
        'grade': 1  # include grade
    }))
    
    formatted_data = []
    for post in matched_posts:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Date', ''),
            'URL': post.get('URL', ''),
            'Username': post.get('Username', ''),
            'Comment': post.get('Comment', ''),
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)

    return jsonify({'status': 'success', 'result_data': formatted_data})

if __name__ == "__main__":
    app.run()
    