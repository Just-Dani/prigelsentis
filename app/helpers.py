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

df_stopwords, df_slang, df_lexicon, lexicon_dict, df_corpus, corpus_words, stemmer = load_data()


def cleaning(text):
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
    elongated_words = re.findall(r'\b\w*(?:(\w)\1{2,})\w*\b', text)
    for word in elongated_words:
        replacement = word[0]
        text = re.sub(r'\b' + re.escape(word) + r'\b', replacement, text)
    return text

def tokenize(text):
    text = word_tokenize(text)
    print("Tokenized Text:", text)
    return text

def translate_slang(text_list):
    translated_list = []
    for text in text_list:
        words = text.split()
        translated_words = []
        for word in words:
            if word in df_slang['singkatan'].tolist():
                translated_words.append(df_slang[df_slang['singkatan'] == word]['kata'].values[0])
            else:
                translated_words.append(word)
        translated_list.append(' '.join(translated_words))
    return translated_list

def remove_stopwords(tokens):
    filtered_words = [word for word in tokens if word.lower() not in df_stopwords['stopword'].values]
    print("Filtered Words:", filtered_words)
    return filtered_words

def stemming(tokens):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stemming_tokens = [stemmer.stem(token) for token in tokens]
    stemming_words = ' '.join(stemming_tokens)
    print("Stemmed Words:", stemming_words)
    return stemming_words

def text_with_ensemble(text):
    model_dir = os.path.join('app', 'models')
    ensemble_model_path = os.path.join(model_dir, 'ensemble_model4.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer1.pkl')
    ensemble_model = joblib.load(ensemble_model_path)
    vectorizer = joblib.load(vectorizer_path)
    text_vectorized = vectorizer.transform([text])
    print("Text Vectorized Shape:", text_vectorized.shape)  # Debugging: Print shape of the vectorized text
    prediction = ensemble_model.predict(text_vectorized)
    print("Prediction:", prediction)  # Debugging: Print prediction
    return prediction[0]

def calculate_sentiment_score(clean_text):
    words = clean_text.split()
    score = 0
    for word in words:
        if word in lexicon_dict:
            score += lexicon_dict[word]
    return score

def add_lexicon_grade(data, text_column):
    grade_list = []
    for index, row in data.iterrows():
        text = row[text_column]
        clean_text = cleaning(text)
        clean_tokens = tokenize(clean_text)
        clean_tokens = translate_slang(clean_tokens)
        clean_tokens = remove_stopwords(clean_tokens)
        clean_text = stemming(clean_tokens)
        sentiment_score = calculate_sentiment_score(clean_text)
        grade_list.append(sentiment_score)
    data['grade'] = grade_list
    return data

def proses_sentimen(data):
    sentimen_list = []
    for index, row in data.iterrows():
        full_text = row['full_text']
        print("\nOriginal Text:", full_text) 
        full_text = cleaning(full_text)
        print("Cleaned Text:", full_text)# Debugging: Print original text
        clean_tokens = tokenize(full_text)
        clean_tokens = translate_slang(clean_tokens)
        clean_tokens = remove_stopwords(clean_tokens)
        clean_text = stemming(clean_tokens)
        sentiment = text_with_ensemble(clean_text)
        sentimen_list.append(sentiment)
    data['sentimen'] = sentimen_list
    data = add_lexicon_grade(data, 'full_text')
    return data

def proses_sentimen_instagram(data):
    sentimen_list = []
    for index, row in data.iterrows():
        comment_text = row['Comment']
        clean_tokens = tokenize(comment_text)
        clean_tokens = translate_slang(clean_tokens)
        clean_tokens = remove_stopwords(clean_tokens)
        clean_text = stemming(clean_tokens)
        sentiment = text_with_ensemble(clean_text)
        sentimen_list.append(sentiment)
    data['sentimen'] = sentimen_list
    data = add_lexicon_grade(data, 'Comment')
    return data

def proses_sentimen_facebook(data):
    sentimen_list = []
    for index, row in data.iterrows():
        comment_text = row['Comment']
        clean_tokens = tokenize(comment_text)
        clean_tokens = translate_slang(clean_tokens)
        clean_tokens = remove_stopwords(clean_tokens)
        clean_text = stemming(clean_tokens)
        sentiment = text_with_ensemble(clean_text)
        sentimen_list.append(sentiment)
    data['sentimen'] = sentimen_list
    data = add_lexicon_grade(data, 'Comment')
    return data


def tabel_sentimen(tweets_collection):    
    tweets_cursor = tweets_collection.find({}, {'_id': 1, 'full_text': 1})
    data = pd.DataFrame(list(tweets_cursor))
    if 'full_text' in data.columns:
        data['full_text'] = data['full_text'].astype(str)
        data = proses_sentimen(data)
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            tweets_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
    return data

def tabel_sentimen_instagram(insta_collection):
    insta_cursor = insta_collection.find({}, {'_id': 1, 'Comment': 1})
    data = pd.DataFrame(list(insta_cursor))
    if 'Comment' in data.columns:
        data['Comment'] = data['Comment'].astype(str)
        data = proses_sentimen_instagram(data)
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            insta_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
    return data


def tabel_sentimen_facebook(facebook_collection):
    facebook_cursor = facebook_collection.find({}, {'_id': 1, 'Comment': 1})
    data = pd.DataFrame(list(facebook_cursor))
    if 'Comment' in data.columns:
        data['Comment'] = data['Comment'].astype(str)
        data = proses_sentimen_facebook(data)
        for index, row in data.iterrows():
            sentimen = row['sentimen']
            grade = row['grade']
            facebook_collection.update_one({'_id': row['_id']}, {'$set': {'sentimen': sentimen, 'grade': grade}})
    return data
# # Baca data dari file CSV
# def load_test_data(file_path):
#     data = pd.read_csv(file_path)
#     return data

# # Tes proses sentiment
# def test_proses_sentimen(file_path):
#     test_data = load_test_data(file_path)
#     if 'full_text' in test_data.columns:
#         test_data['full_text'] = test_data['full_text'].astype(str)
#         processed_data = proses_sentimen(test_data)
#         print(processed_data)
#     elif 'Comment' in test_data.columns:
#         test_data['Comment'] = test_data['Comment'].astype(str)
#         processed_data = proses_sentimen_instagram(test_data)
#         print(processed_data)
#     else:
#         print("Kolom 'full_text' atau 'Comment' tidak ditemukan dalam data uji.")

# # Uji dengan data file 'test_data.csv'
# test_proses_sentimen('book1.csv')


def schedule_sentimen(tweets_collection, insta_collection, facebook_collection, run_immediately=False):
    # Schedule the tasks for daily execution at 13:30
    schedule.every().day.at("13:30").do(tabel_sentimen, tweets_collection=tweets_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_instagram, insta_collection=insta_collection)
    schedule.every().day.at("13:30").do(tabel_sentimen_facebook, facebook_collection=facebook_collection)
    # If run_immediately is True, execute the tasks right now
    if run_immediately:
        print("Running sentiment analysis immediately...")
        tabel_sentimen(tweets_collection)  # Process Twitter data
        tabel_sentimen_instagram(insta_collection)  # Process Instagram data
        tabel_sentimen_facebook(facebook_collection) # Process Facebook data
    
    # Keep the scheduler running in the background
    while True:
        schedule.run_pending()
        time.sleep(60)
                
# sentiment_score = calculate_sentiment_score(clean_text)
# print("Sentiment Score:", sentiment_score)  # Debugging: Print sentiment score

# # Classify sentiment based on score
# if sentiment_score > 0:
#     sentiment = 'Positive'
# elif sentiment_score < 0:
#     sentiment = 'Negative'
# else:
#     sentiment = 'Neutral'
# sentimen_list.append(sentiment)