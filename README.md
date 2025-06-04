# SENTIS2025
Jika belum ada folder SENTIS dengan git, lakukan: <br />
git clone https://github.com/Just-Dani/prigelsentis.git

Jika sudah ada tapi belum up to date, lakukan: <br />
git pull

NEW <br />
Crawling system flowchart <br />
![alt text](https://github.com/Just-Dani/prigelsentis/blob/main/facebookflowchart.png?raw=true)

Notes <br />
To start the application, run "py run.py" <br />
To start the model immediately, change line [32] False into True <br />
From this: <br />
sentiment_thread = threading.Thread(target=schedule_sentimen, args=(tweets_collection, insta_collection, facebook_collection, False)) <br /> <br />
To this: <br />
sentiment_thread = threading.Thread(target=schedule_sentimen, args=(tweets_collection, insta_collection, facebook_collection, True)) <br />
    
To start facebook crawling manually, run "py ./app/crawling/facebook_scrapper.py" <br />

Cara untuk push update ke github:
1. git branch
2. git add .
3. git commit -m "message"
4. git pull
5. git push
