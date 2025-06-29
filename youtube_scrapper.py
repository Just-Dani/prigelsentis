from googleapiclient.discovery import build
import csv
import datetime

# Ganti dengan API key dari Google Developer Console
API_KEY = 'AIzaSyAVdb9CUY2ZUiRDvvWNuXI8Tx_1xyAC4yM'

# Inisialisasi API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_id_from_url(url):
    """Ekstrak ID video dari URL YouTube"""
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    else:
        raise ValueError('URL video tidak valid')

def get_all_comments(video_url):
    video_id = get_video_id_from_url(video_url)
    comments_data = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request:
        response = request.execute()

        for item in response['items']:
            snippet = item['snippet']['topLevelComment']['snippet']
            published_at = snippet['publishedAt']
            author = snippet['authorDisplayName']
            comment = snippet['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            comment_link = f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}"

            comments_data.append([
                published_at,
                comment_link,
                author,
                comment
            ])

        request = youtube.commentThreads().list_next(request, response)

    return comments_data

def save_comments_to_csv(comments, filename='youtube_comments.csv'):
    header = ['Tanggal', 'Link Komentar', 'Nama Akun', 'Isi Komentar']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(comments)

if __name__ == '__main__':
    video_url = input("Masukkan URL video YouTube: ")
    try:
        all_comments = get_all_comments(video_url)
        save_comments_to_csv(all_comments)
        print(f"Berhasil menyimpan {len(all_comments)} komentar ke dalam file 'youtube_comments.csv'")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
