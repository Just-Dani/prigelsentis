import pymongo
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from pymongo import MongoClient
from bson import json_util, ObjectId
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import secrets
from .helpers import schedule_sentimen # Mengimpor schedule_sentimen dari helpers

# Menginisialisasi Blueprint
bp = Blueprint('main', __name__)

# Menginisialisasi koneksi MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.db_analisis_sentimen
users_collection = db.users
tweets_collection = db.tweets
instagram_collection = db.instagram
facebook_collection = db.facebook
tiktok_collection = db.tiktok
youtube_collection = db.youtube

# Inisialisasi Bcrypt (akan diinisialisasi di create_app di __init__.py)
bcrypt = Bcrypt() 

# Rute untuk menghapus data tweet
@bp.route('/delete_tweet_data/<string:id>', methods=['DELETE'])
@login_required 
def delete_tweet_data(id):
    result = tweets_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

# Rute untuk menghapus data Instagram
@bp.route('/delete_instagram_data/<string:id>', methods=['DELETE'])
@login_required 
def delete_instagram_data(id):
    result = instagram_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

# Rute untuk menghapus data Facebook
@bp.route('/delete_facebook_data/<string:id>', methods=['DELETE'])
@login_required 
def delete_facebook_data(id):
    result = facebook_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

# Rute untuk menghapus data TikTok
@bp.route('/delete_tiktok_data/<string:id>', methods=['DELETE'])
@login_required
def delete_tiktok_data(id):
    result = tiktok_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

# Rute untuk menghapus data YouTube
@bp.route('/delete_youtube_data/<string:id>', methods=['DELETE'])
@login_required
def delete_youtube_data(id):
    result = youtube_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Data not found'}), 404

# Rute utama, mengarahkan ke halaman login
@bp.route("/", methods=['GET'])
def index():
    return render_template('login.html')

# Rute pendaftaran pengguna baru
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = users_collection.find_one({'username': username})

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('main.register')) 
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'username': username, 'password': hashed_password})

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('main.login')) 

    return render_template('register.html')

# Rute login pengguna
@bp.route("/login", methods=['GET', 'POST'])
def login():
    from app import load_user 
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = users_collection.find_one({'username': username})

        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = load_user(str(user_data['_id'])) 
            login_user(user) 
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard')) 
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('main.index')) 

    return render_template('login.html')

# Rute logout pengguna
@bp.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index')) 

# Rute dashboard (Twitter)
@bp.route('/dashboard')
@login_required 
def dashboard():
    return render_template('index-twit.html')

# Rute Instagram
@bp.route('/instagram')
@login_required 
def instagram():
    return render_template('index-insta.html')

# Rute Facebook
@bp.route('/facebook')
@login_required 
def facebook():
    return render_template('index-face.html')

# Rute TikTok
@bp.route('/tiktok')
@login_required
def tiktok():
    return render_template('index-tiktok.html')

# Rute YouTube
@bp.route('/youtube')
@login_required
def youtube():
    return render_template('index-youtube.html')

# Rute Instagram - Positif
@bp.route('/instagram-positif')
@login_required
def instagram_positif():
    return render_template('positif-insta.html')

# Rute Instagram - Negatif
@bp.route('/instagram-negatif')
@login_required
def instagram_negatif():
    return render_template('negatif-insta.html')

# Rute Instagram - Netral
@bp.route('/instagram-netral')
@login_required
def instagram_netral():
    return render_template('netral-insta.html')

# Rute Twitter - Positif
@bp.route('/twitter-positif')
@login_required
def twitter_positif():
    return render_template('positif-tweet.html')

# Rute Twitter - Negatif
@bp.route('/twitter-negatif')
@login_required
def twitter_negatif():
    return render_template('negatif-tweet.html')

# Rute Twitter - Netral
@bp.route('/twitter-netral')
@login_required
def twitter_netral():
    return render_template('netral-tweet.html')

# Rute Facebook - Positif
@bp.route('/facebook-positif')
@login_required
def facebook_positif():
    return render_template('positif-face.html')

# Rute Facebook - Negatif
@bp.route('/facebook-negatif')
@login_required
def facebook_negatif():
    return render_template('negatif-face.html')

# Rute Facebook - Netral
@bp.route('/facebook-netral')
@login_required
def facebook_netral():
    return render_template('netral-face.html')

# Rute TikTok - Positif
@bp.route('/tiktok-positif')
@login_required
def tiktok_positif():
    return render_template('positif-tiktok.html')

# Rute TikTok - Negatif
@bp.route('/tiktok-negatif')
@login_required
def tiktok_negatif():
    return render_template('negatif-tiktok.html')

# Rute TikTok - Netral
@bp.route('/tiktok-netral')
@login_required
def tiktok_netral():
    return render_template('netral-tiktok.html')

# Rute YouTube - Positif
@bp.route('/youtube-positif')
@login_required
def youtube_positif():
    return render_template('positif-youtube.html')

# Rute YouTube - Negatif
@bp.route('/youtube-negatif')
@login_required
def youtube_negatif():
    return render_template('negatif-youtube.html')

# Rute YouTube - Netral
@bp.route('/youtube-netral')
@login_required
def youtube_netral():
    return render_template('netral-youtube.html')

# Rute untuk mendapatkan data tweet
@bp.route('/data', methods=['GET'])
@login_required
def get_data():
    print("Mengambil data tweet dari MongoDB...")
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
    print(f"Mengembalikan {len(formatted_data)} data tweet.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mencari tweet
@bp.route('/search_tweets', methods=['GET'])
@login_required
def search_tweets():
    search_query = request.args.get('q', '').lower()
    print(f"Mencari tweet dengan query: {search_query}")
    matched_tweets = list(tweets_collection.find({'full_text': {'$regex': search_query, '$options': 'i'}}, {'_id': 1, 'created_at': 1, 'full_text': 1, 'sentimen': 1, 'tweet_url': 1, 'grade': 1}))
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
    print(f"Mengembalikan {len(formatted_data)} data tweet yang cocok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mendapatkan data Instagram
@bp.route('/instagram_data', methods=['GET'])
@login_required
def get_instagram_data():
    print("Mengambil data Instagram dari MongoDB...")
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
    print(f"Mengembalikan {len(formatted_data)} data Instagram.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mencari data Instagram
@bp.route('/search_instagram', methods=['GET'])
@login_required
def search_instagram():
    search_query = request.args.get('q', '').lower()
    print(f"Mencari Instagram dengan query: {search_query}")
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
    print(f"Mengembalikan {len(formatted_data)} data Instagram yang cocok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mendapatkan data Facebook
@bp.route('/facebook_data', methods=['GET'])
@login_required
def get_facebook_data():
    print("Mengambil data Facebook dari MongoDB...")
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
    print(f"Mengembalikan {len(formatted_data)} data Facebook.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mencari data Facebook
@bp.route('/search_facebook', methods=['GET'])
@login_required
def search_facebook():
    search_query = request.args.get('q', '').lower()
    print(f"Mencari Facebook dengan query: {search_query}")
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
            'Comment': post.get('Comment', ''), # Perbaikan: Gunakan 'Comment' dari MongoDB (sesuai FB)
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)
    print(f"Mengembalikan {len(formatted_data)} data Facebook yang cocok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mendapatkan data TikTok
@bp.route('/tiktok_data', methods=['GET'])
@login_required
def get_tiktok_data():
    print("Mengambil data TikTok dari MongoDB...")
    # Mengambil semua field yang mungkin relevan dari koleksi TikTok
    tiktok_data = list(tiktok_collection.find({}, {
        '_id': 1,
        'Link': 1,      # Sesuai dengan yang terlihat di Compass
        'Nama Akun': 1, # <-- Perbaikan: Gunakan 'Nama Akun' dari MongoDB
        'Komentar': 1,  # Sesuai dengan yang terlihat di Compass
        'Tanggal': 1,   # <-- Perbaikan: Gunakan 'Tanggal' dari MongoDB
        'sentimen': 1,  # Field yang ditambahkan oleh proses sentimen
        'grade': 1      # Field yang ditambahkan oleh proses sentimen
    }))
    
    formatted_data = []
    for post in tiktok_data:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Tanggal', ''), # <-- Perbaikan: Memetakan 'Tanggal' ke 'Date'
            'URL': post.get('Link', ''), 
            'Username': post.get('Nama Akun', ''), # <-- Perbaikan: Memetakan 'Nama Akun' ke 'Username'
            'Comment': post.get('Komentar', ''), 
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)
    print(f"Mengembalikan {len(formatted_data)} data TikTok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mencari data TikTok
@bp.route('/search_tiktok', methods=['GET'])
@login_required
def search_tiktok():
    search_query = request.args.get('q', '').lower()
    print(f"Mencari TikTok dengan query: {search_query}")
    # Mencari di kolom 'Username' atau 'Komentar'
    matched_posts = list(tiktok_collection.find({'$or': [
        {'Nama Akun': {'$regex': search_query, '$options': 'i'}}, # <-- Perbaikan: Mencari di 'Nama Akun'
        {'Komentar': {'$regex': search_query, '$options': 'i'}} 
    ]}, {
        '_id': 1,
        'Link': 1,
        'Nama Akun': 1, # <-- Perbaikan: Gunakan 'Nama Akun'
        'Komentar': 1,
        'Tanggal': 1,   # <-- Perbaikan: Gunakan 'Tanggal'
        'sentimen': 1,
        'grade': 1
    }))
    
    formatted_data = []
    for post in matched_posts:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Tanggal', ''), # <-- Perbaikan: Memetakan 'Tanggal' ke 'Date'
            'URL': post.get('Link', ''),
            'Username': post.get('Nama Akun', ''), # <-- Perbaikan: Memetakan 'Nama Akun' ke 'Username'
            'Comment': post.get('Komentar', ''), 
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)
    print(f"Mengembalikan {len(formatted_data)} data TikTok yang cocok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mendapatkan data YouTube
@bp.route('/youtube_data', methods=['GET'])
@login_required
def get_youtube_data():
    print("Mengambil data YouTube dari MongoDB...")
    # Mengambil semua field yang mungkin relevan dari koleksi YouTube
    youtube_data = list(youtube_collection.find({}, {
        '_id': 1,
        'Link': 1,      
        'Nama Akun': 1, # <-- Perbaikan: Gunakan 'Nama Akun' dari MongoDB
        'Komentar': 1,  
        'Tanggal': 1,   # <-- Perbaikan: Gunakan 'Tanggal' dari MongoDB
        'sentimen': 1,  
        'grade': 1      
    }))
    
    formatted_data = []
    for post in youtube_data:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Tanggal', ''), # <-- Perbaikan: Memetakan 'Tanggal' ke 'Date'
            'URL': post.get('Link', ''), 
            'Username': post.get('Nama Akun', ''), # <-- Perbaikan: Memetakan 'Nama Akun' ke 'Username'
            'Comment': post.get('Komentar', ''), 
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)
    print(f"Mengembalikan {len(formatted_data)} data YouTube.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

# Rute untuk mencari data YouTube
@bp.route('/search_youtube', methods=['GET'])
@login_required
def search_youtube():
    search_query = request.args.get('q', '').lower()
    print(f"Mencari YouTube dengan query: {search_query}")
    # Mencari di kolom 'Username' atau 'Komentar'
    matched_posts = list(youtube_collection.find({'$or': [
        {'Nama Akun': {'$regex': search_query, '$options': 'i'}}, # <-- Perbaikan: Mencari di 'Nama Akun'
        {'Komentar': {'$regex': search_query, '$options': 'i'}} 
    ]}, {
        '_id': 1,
        'Link': 1,
        'Nama Akun': 1, # <-- Perbaikan: Gunakan 'Nama Akun'
        'Komentar': 1,
        'Tanggal': 1,   # <-- Perbaikan: Gunakan 'Tanggal'
        'sentimen': 1,
        'grade': 1
    }))
    
    formatted_data = []
    for post in matched_posts:
        formatted_post = {
            '_id': str(post['_id']),
            'Date': post.get('Tanggal', ''), # <-- Perbaikan: Memetakan 'Tanggal' ke 'Date'
            'URL': post.get('Link', ''),
            'Username': post.get('Nama Akun', ''), # <-- Perbaikan: Memetakan 'Nama Akun' ke 'Username'
            'Comment': post.get('Komentar', ''), 
            'sentimen': post.get('sentimen', ''),
            'grade': post.get('grade', '')
        }
        formatted_data.append(formatted_post)
    print(f"Mengembalikan {len(formatted_data)} data YouTube yang cocok.")
    return jsonify({'status': 'success', 'result_data': formatted_data})

