import pandas as pd
from pymongo import MongoClient
import os

# Konfigurasi MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'db_analisis_sentimen'

# Path ke direktori data CSV Anda
# Sesuaikan path ini jika file CSV Anda berada di lokasi yang berbeda
# Asumsi: skrip ini dijalankan dari direktori root proyek 'Sentiment Analysis - Project'
# dan file CSV berada di subdirektori 'tiktok-data' dan 'youtube-data'
tiktok_csv_path = 'tiktok-data/tiktok_comment_data.csv'
youtube_csv_path = 'youtube-data/youtube_comment_data.csv'

def import_csv_to_mongo(csv_file_path, collection_name, client):
    """
    Mengimpor data dari file CSV ke koleksi MongoDB tertentu.
    """
    db = client[DATABASE_NAME]
    collection = db[collection_name]

    print(f"Memulai impor data dari {csv_file_path} ke koleksi {collection_name}...")

    if not os.path.exists(csv_file_path):
        print(f"Error: File CSV tidak ditemukan di {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path)
        # Mengisi nilai NaN dengan string kosong untuk menghindari masalah None di MongoDB
        df = df.fillna('') 

        # Mengubah DataFrame menjadi daftar kamus (dokumen JSON)
        data_to_insert = df.to_dict(orient='records')

        if data_to_insert:
            # Menghapus data yang ada di koleksi sebelum memasukkan yang baru (opsional, untuk menghindari duplikasi)
            # Anda bisa mengaktifkan baris di bawah ini jika Anda ingin membersihkan koleksi sebelum impor baru
            # collection.delete_many({}) 
            # print(f"Menghapus data lama dari koleksi {collection_name}...")

            collection.insert_many(data_to_insert)
            print(f"Berhasil mengimpor {len(data_to_insert)} dokumen ke koleksi {collection_name}.")
        else:
            print(f"Tidak ada data untuk diimpor dari {csv_file_path}.")

    except Exception as e:
        print(f"Terjadi kesalahan saat mengimpor data dari {csv_file_path}: {e}")

if __name__ == "__main__":
    mongo_client = None
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_client.admin.command('ping') # Uji koneksi
        print("Koneksi MongoDB berhasil!")

        # Impor data TikTok
        import_csv_to_mongo(tiktok_csv_path, 'tiktok', mongo_client)

        # Impor data YouTube
        import_csv_to_mongo(youtube_csv_path, 'youtube', mongo_client)

    except Exception as e:
        print(f"Gagal terhubung ke MongoDB atau terjadi kesalahan: {e}")
    finally:
        if mongo_client:
            mongo_client.close()
            print("Koneksi MongoDB ditutup.")

