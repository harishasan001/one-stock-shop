# news_data.py

import requests
import json
from typing import List
from datetime import datetime, timedelta
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# nltk.download('vader_lexicon')

NEWS_API_KEY = "96975858054e43609b5280fae30c01d1"

def get_stock_news(symbol: str, api_key: str) -> List[dict]:
    today = datetime.now().date()
    thirty_days_ago = (today - timedelta(days=30)).isoformat()

    url = f"https://newsapi.org/v2/everything?q=${symbol}&from={thirty_days_ago}&sortBy=relevance&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        raise NewsAPIError(f"Error occurred! Status code: {response.status_code}")

    news_data = json.loads(response.text)
    
    news_articles = [
        {
            "title": article["title"],
            "url": article["url"],
            "image": article["urlToImage"],
            "sentiment": analyze_sentiment(article["title"]),
            "sentiment_score": SentimentIntensityAnalyzer().polarity_scores(article["title"])["compound"],
        }
        for article in news_data["articles"]
    ]

    return news_articles[:5]

def analyze_sentiment(title: str) -> str:
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(title)["compound"]

    if sentiment_score >= 0.05:
        return "Positive"
    elif sentiment_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"
    
def get_overall_sentiment(news_articles: List[dict]) -> dict:
    if not news_articles:
        return {"sentiment": "N/A", "color": "gray"}

    total_score = sum(article["sentiment_score"] for article in news_articles)
    average_score = total_score / len(news_articles)

    if average_score >= 0.05:
        return {"sentiment": "Positive", "color": "green"}
    elif average_score <= -0.05:
        return {"sentiment": "Negative", "color": "red"}
    else:
        return {"sentiment": "Neutral", "color": "gray"}

def sentiment_color(sentiment: str) -> str:
    if sentiment == "Positive":
        return "green"
    elif sentiment == "Negative":
        return "red"
    else:
        return "gray"

class NewsAPIError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)