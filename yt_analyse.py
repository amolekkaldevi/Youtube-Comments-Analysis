import os
import re
from datetime import datetime as dt
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd
from textblob import TextBlob
from flask import Flask, request, jsonify, send_file
from flask import Flask, send_from_directory

app = Flask(__name__)

comments = []
today = dt.today().strftime('%d-%m-%Y')

load_dotenv()
API_KEY = os.getenv("API_KEY")

youtube = build(
    "youtube", "v3", developerKey=API_KEY
)

def comment_threads(channelID):
    comments_list = []

    request = youtube.commentThreads().list(
        part='snippet',
        videoId=channelID,
    )
    response = request.execute()

    comments_list.extend(process_comments(response['items']))

    while response.get('nextPageToken', None):
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=channelID,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        comments_list.extend(process_comments(response['items']))

    print(f"Finished fetching comments for {channelID}.{len(comments_list)} comments found.")

    return comments_list

def process_comments(response_items):
    for res in response_items:
        comment = res['snippet']['topLevelComment']['snippet']
        comments.append(comment)

    print(f'Finished processing {len(comments)} comments.')
    return comments

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity == 0:
        return 'neutral'
    else:
        return 'negative'
    

@app.route('/script.js')
def serve_js():
    js_dir = os.path.dirname(__file__)
    return send_from_directory(js_dir, 'script.js')

@app.route('/styles.css')
def serve_css():
    css_dir = os.path.dirname(__file__)
    return send_from_directory(css_dir, 'styles.css')



@app.route('/')
def index():
    return send_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    youtube_link = request.json.get('youtubeLink')
    
    pattern = r"(?<=v=)[\w-]+"
    match = re.search(pattern, youtube_link)
    if match:
        key_value = match.group(0)
        print("Video ID:", key_value)
    else:
        return jsonify({"error": "Video ID not found in the URL."})

    comments_data = comment_threads(key_value)
    data_df = pd.DataFrame(comments_data, columns=['textDisplay'])

    data_df['sentiment'] = data_df['textDisplay'].apply(analyze_sentiment)

    sentiment_counts = data_df['sentiment'].value_counts(normalize=True) * 100
    positive_percentage = round(sentiment_counts.get('positive', 0),2)
    neutral_percentage = round(sentiment_counts.get('neutral', 0),2)
    negative_percentage = round(sentiment_counts.get('negative', 0),2)

    return jsonify({
        "positive": positive_percentage,
        "neutral": neutral_percentage,
        "negative": negative_percentage
    })

if __name__ == "__main__":
    app.run(debug=True)
