import os
import praw
import time
import requests
import openai
from datetime import datetime

# === ENV Variables ===
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# === Init Reddit
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=REDDIT_USER_AGENT,
)

KEYWORDS = ["calls", "puts", "option", "IV", "0DTE", "bull", "bear", "gamma", "SPY", "GME", "NVDA", "TSLA"]
SENT_POSTS = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def ai_score_post(title):
    prompt = f"""Analyze this post and return:
1. Relevance to stock market (0-100)
2. Sentiment (Bullish, Bearish, Neutral)

Post: "{title}"
Only respond in format: 
Relevance: ##% | Sentiment: <sentiment>
"""
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return res['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Relevance: 0% | Sentiment: Unknown (Error: {e})"

def watch_wsb_ai():
    top_insights = []
    subreddit = reddit.subreddit("wallstreetbets")

    for post in subreddit.new(limit=25):
        if post.id not in SENT_POSTS:
            title = post.title.strip()
            if any(k.lower() in title.lower() for k in KEYWORDS):
                score = ai_score_post(title)
                timestamp = datetime.now().strftime("%I:%M %p")
                post_info = f"Ticker: [guess]\nMessage: \"{title}\"\n{score}\nTime: {timestamp} | Post: {post.shortlink}\n"
                top_insights.append((score, post_info))
                SENT_POSTS.add(post.id)

    if top_insights:
        top_insights.sort(reverse=True)
        top_3 = [i[1] for i in top_insights[:3]]
        full_alert = "[NOVA WSB WATCHER]\n\n" + "\n—\n".join(top_3)
        send_telegram(full_alert)

if __name__ == "__main__":
    send_telegram("✅ Nova WSB AI Watcher is now live.")
    while True:
        try:
            watch_wsb_ai()
            time.sleep(3600)  # every hour
        except Exception as e:
            send_telegram(f"⚠️ Error: {e}")
            time.sleep(60)
