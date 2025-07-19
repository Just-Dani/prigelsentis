import re
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import string
import os
import joblib
import schedule
import time

def load_data():
    """
    Memuat data yang diperlukan untuk preprocessing teks dari file CSV.
    Data yang dimuat meliputi stopwords, kamus singkatan, leksikon sentimen, dan korpus kata.
    Juga menginisialisasi stemmer Sastrawi.
    """
    module_path = os.path.abspath(__file__)
    data_directory = os.path.join(os.path.dirname(module_path), 'data')

    df_stopwords = pd.read_csv(os.path.join(data_directory, 'stopwords-id.csv'), header=None, names=['stopword'])
    df_slang = pd.read_csv(os.path.join(data_directory, 'kamus-singkatan.csv'), delimiter=';', names=['singkatan', 'kata'])
    df_lexicon = pd.read_csv(os.path.join(data_directory, 'lexicon-inset.csv'))
    lexicon_dict = dict(zip(df_lexicon['word'], df_lexicon['weight']))
    df_corpus = pd.read_csv(os.path.join(data_directory, 'corpus.csv'))
    corpus_words = df_corpus['kata'].tolist()

    stemmer = StemmerFactory().create_stemmer()
    return df_stopwords, df_slang, df_lexicon, lexicon_dict, df_corpus, corpus_words, stemmer

# Memuat data sekali saat modul diimpor
df_stopwords, df_slang, df_lexicon, lexicon_dict, df_corpus, corpus_words, stemmer = load_data()


def cleaning(text):
    """
    Melakukan pembersihan teks:
    - Menghapus emoji
    - Mengganti pola tertentu
    - Menghapus mention (@username), karakter non-alfanumerik, URL, dan RT
    - Menghapus spasi berlebih, angka, dan karakter berulang
    - Mengubah teks menjadi huruf kecil
    """
    if not isinstance(text, str):
        return "" # Mengembalikan string kosong jika input bukan string
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r' ', text)
    text = text.replace('-ness', '').replace('-jualness', '')
    text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text)
    text = re.sub(r'^RT[\s]+', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = re.sub(r'/n', ' ', text)
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[0-9]+', '', text)
    text = re.sub(r'(?<!\bunnes)(\w)(\1+)(?=\s|[\.,!])', r'\1', text)
    text = text.strip(' ')
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = text.lower()  
    return text

def replace_word(text):
    """
    Mengganti kata yang memanjang (misal: "baaaik" menjadi "baik").
    """
    elongated_words = re.findall(r'\b\w*(?:(\w)\1{2,})\w*\b', text)
    for word in elongated_words:
        replacement = word[0]
        text = re.sub(r'\b' + re.escape(word) + r'\b', replacement, text)
    return text

def tokenize(text):
    """
    Melakukan tokenisasi teks menjadi daftar kata.
    """
    text = word_tokenize(text)
    return text

def translate_slang(text_list):
    """
    Menerjemahkan kata slang dalam daftar kata menggunakan kamus singkatan.
    """
    translated_list = []
    for text_item in text_list: 
        words = text_item.split() 
        translated_words = []
        for word in words:
            if word in df_slang['singkatan'].tolist():
                translated_words.append(df_slang[df_slang['singkatan'] == word]['kata'].values[0])
            else:
                translated_words.append(word)
        translated_list.append(' '.join(translated_words))
    return translated_list

def remove_stopwords(tokens):
    """
    Menghapus stopword dari daftar token.
    """
    filtered_words = [word for word in tokens if word.lower() not in df_stopwords['stopword'].values]
    return filtered_words

def stemming(tokens):
    """
    Melakukan stemming pada token menggunakan Sastrawi Stemmer.
    """
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stemming_tokens = [stemmer.stem(token) for token in tokens]
    stemming_words = ' '.join(stemming_tokens)
    return stemming_words

def text_with_ensemble(text):
    """
    Memuat model ensemble dan vectorizer, lalu memprediksi sentimen dari teks.
    """
    model_dir = os.path.join('app', 'models')
    ensemble_model_path = os.path.join(model_dir, 'ensemble_model4.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer1.pkl')
    
    if not os.path.exists(ensemble_model_path):
        print(f"Error: Model ensemble tidak ditemukan di {ensemble_model_path}")
        return "Netral" # Fallback
    if not os.path.exists(vectorizer_path):
        print(f"Error: Vectorizer tidak ditemukan di {vectorizer_path}")
        return "Netral" # Fallback

    ensemble_model = joblib.load(ensemble_model_path)
    vectorizer = joblib.load(vectorizer_path)
    text_vectorized = vectorizer.transform([text])
    prediction = ensemble_model.predict(text_vectorized)
    return prediction[0]

def calculate_sentiment_score(clean_text):
    """
    Menghitung skor sentimen berdasarkan leksikon.
    """
    words = clean_text.split()
    score = 0
    for word in words:
        if word in lexicon_dict:
            score += lexicon_dict[word]
    return score

def add_lexicon_grade(data, text_column):
    """
    Menambahkan kolom 'grade' ke DataFrame berdasarkan skor leksikon dari teks.
    """
    grade_list = []
    for index, row in data.iterrows():
        text = row[text_column]
        clean_text = cleaning(text)
        clean_tokens = tokenize(clean_text)
        clean_tokens_translated_str = translate_slang([' '.join(clean_tokens)])[0] 
        clean_tokens_filtered = remove_stopwords(clean_tokens_translated_str.split()) 
        clean_text_stemmed = stemming(clean_tokens_filtered)
        sentiment_score = calculate_sentiment_score(clean_text_stemmed)
        grade_list.append(sentiment_score)
    data['grade'] = grade_list
    return data

def proses_sentimen(data, text_column_name):
    """
    Memproses sentimen untuk data dari berbagai platform.
    Menerima nama kolom teks sebagai argumen.
    """
    sentimen_list = []
    for index, row in data.iterrows():
        original_text = row[text_column_name]
        cleaned_text = cleaning(original_text)
        tokenized_text = tokenize(cleaned_text)
        translated_text_str = translate_slang([' '.join(tokenized_text)])[0] 
        filtered_tokens = remove_stopwords(translated_text_str.split()) 
        stemmed_text = stemming(filtered_tokens)
        sentiment = text_with_ensemble(stemmed_text)
        sentimen_list.append(sentiment)
    data['sentimen'] = sentimen_list
    data = add_lexicon_grade(data, text_column_name)
    return data


def tabel_sentimen(tweets_collection):    
    """
    Mengambil data tweet dari MongoDB, memproses sentimen, dan memperbarui koleksi.
    """
    print("Memulai proses sentimen untuk tweets...")
    tweets_cursor = tweets_collection.find({}, {'_id': 1, 'full_text': 1})
    data = pd.DataFrame(list(tweets_cursor))
    if not data.empty and 'full_text' in data.columns:
        data['full_text'] = data['full_text'].astype(str)
        data = proses_sentimen(data, 'full_text')
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            tweets_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
        print(f"Berhasil memperbarui {len(data)} dokumen di koleksi tweets.")
    else:
        print("Koleksi tweets kosong atau kolom 'full_text' tidak ditemukan. Tidak ada sentimen yang diproses.")
    return data

def tabel_sentimen_instagram(insta_collection):
    """
    Mengambil data Instagram dari MongoDB, memproses sentimen, dan memperbarui koleksi.
    """
    print("Memulai proses sentimen untuk instagram...")
    insta_cursor = insta_collection.find({}, {'_id': 1, 'Comment': 1})
    data = pd.DataFrame(list(insta_cursor))
    if not data.empty and 'Comment' in data.columns:
        data['Comment'] = data['Comment'].astype(str)
        data = proses_sentimen(data, 'Comment') # Menggunakan fungsi proses_sentimen umum
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            insta_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
        print(f"Berhasil memperbarui {len(data)} dokumen di koleksi instagram.")
    else:
        print("Koleksi instagram kosong atau kolom 'Comment' tidak ditemukan. Tidak ada sentimen yang diproses.")
    return data


def tabel_sentimen_facebook(facebook_collection):
    """
    Mengambil data Facebook dari MongoDB, memproses sentimen, dan memperbarui koleksi.
    """
    print("Memulai proses sentimen untuk facebook...")
    facebook_cursor = facebook_collection.find({}, {'_id': 1, 'Comment': 1})
    data = pd.DataFrame(list(facebook_cursor))
    if not data.empty and 'Comment' in data.columns:
        data['Comment'] = data['Comment'].astype(str)
        data = proses_sentimen(data, 'Comment') # Menggunakan fungsi proses_sentimen umum
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            facebook_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
        print(f"Berhasil memperbarui {len(data)} dokumen di koleksi facebook.")
    else:
        print("Koleksi facebook kosong atau kolom 'Comment' tidak ditemukan. Tidak ada sentimen yang diproses.")
    return data

def tabel_sentimen_tiktok(tiktok_collection):
    """
    Mengambil data TikTok dari MongoDB, memproses sentimen, dan memperbarui koleksi.
    """
    print("Memulai proses sentimen untuk tiktok...")
    # Mengambil field 'Komentar' dari MongoDB untuk diproses sentimen
    # Juga mengambil 'Tanggal', 'Nama Akun', 'Link' untuk update kembali
    tiktok_cursor = tiktok_collection.find({}, {'_id': 1, 'Komentar': 1, 'Tanggal': 1, 'Nama Akun': 1, 'Link': 1}) 
    data = pd.DataFrame(list(tiktok_cursor))
    if not data.empty and 'Komentar' in data.columns: 
        data['Komentar'] = data['Komentar'].astype(str)
        data = proses_sentimen(data, 'Komentar') # Menggunakan fungsi proses_sentimen umum dengan 'Komentar'
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            tiktok_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
        print(f"Berhasil memperbarui {len(data)} dokumen di koleksi tiktok.")
    else:
        print("Koleksi tiktok kosong atau kolom 'Komentar' tidak ditemukan. Tidak ada sentimen yang diproses.")
    return data

def tabel_sentimen_youtube(youtube_collection):
    """
    Mengambil data YouTube dari MongoDB, memproses sentimen, dan memperbarui koleksi.
    """
    print("Memulai proses sentimen untuk youtube...")
    # Mengambil field 'Komentar' dari MongoDB untuk diproses sentimen
    # Juga mengambil 'Tanggal', 'Nama Akun', 'Link' untuk update kembali
    youtube_cursor = youtube_collection.find({}, {'_id': 1, 'Komentar': 1, 'Tanggal': 1, 'Nama Akun': 1, 'Link': 1}) 
    data = pd.DataFrame(list(youtube_cursor))
    if not data.empty and 'Komentar' in data.columns: 
        data['Komentar'] = data['Komentar'].astype(str)
        data = proses_sentimen(data, 'Komentar') # Menggunakan fungsi proses_sentimen umum dengan 'Komentar'
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            youtube_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
        print(f"Berhasil memperbarui {len(data)} dokumen di koleksi youtube.")
    else:
        print("Koleksi youtube kosong atau kolom 'Komentar' tidak ditemukan. Tidak ada sentimen yang diproses.")
    return data


def schedule_sentimen(tweets_collection, insta_collection, facebook_collection, tiktok_collection, youtube_collection, run_immediately=False):
    """
    Menjadwalkan tugas analisis sentimen untuk berbagai platform media sosial.
    Dapat juga menjalankan analisis sentimen segera jika 'run_immediately' True.
    """
    print("Memulai penjadwalan sentimen...")
    # Menjadwalkan tugas untuk eksekusi harian pada pukul 13:30
    schedule.every().day.at("13:30").do(tabel_sentimen, tweets_collection=tweets_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_instagram, insta_collection=insta_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_facebook, facebook_collection=facebook_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_tiktok, tiktok_collection=tiktok_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_youtube, youtube_collection=youtube_collection)
    
    # Jika run_immediately True, jalankan tugas sekarang
    if run_immediately:
        print("Menjalankan analisis sentimen segera...")
        tabel_sentimen(tweets_collection)  # Proses data Twitter
        tabel_sentimen_instagram(insta_collection)  # Proses data Instagram
        tabel_sentimen_facebook(facebook_collection) # Proses data Facebook
        tabel_sentimen_tiktok(tiktok_collection) # Proses data TikTok
        tabel_sentimen_youtube(youtube_collection) # Proses data YouTube
    
    # Menjaga scheduler tetap berjalan di latar belakang
    while True:
        schedule.run_pending()
        time.sleep(60)

