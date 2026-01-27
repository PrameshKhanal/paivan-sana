import requests
import tweepy
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_twitter_client():
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )
    return client

def fetch_finnish_word_of_the_day(max_retries=3):
    url = "https://www.suomisanakirja.fi/wod.php"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Attempt {attempt + 1}: API returned status {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed - {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
    
    return None

def create_tweet_text(word_data):
    word = word_data.get("word", "N/A")
    definition = word_data.get("definition", "")
    
    tweet = f"🇫🇮 Päivän Sana / Finnish Word of the Day\n\n✨ {word} ✨"
    
    if definition:
        tweet += f"\n\n📖 {definition}"
    
    tweet += "\n\nOsaatko käyttää tätä sanaa lauseessa? 🤔\nCan you use this word in a sentence?"
    tweet += "\n\n#Finnish #Suomi #LearnFinnish #OpiSuomea"
    
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    return tweet

def create_fallback_tweet():
    tweet = "🇫🇮 Päivän Sana / Finnish Word of the Day\n\n"
    tweet += "😢 Ei sanaa tänään / No word today\n\n"
    tweet += "Tarkista huomenna uudelleen!\nCheck back tomorrow!\n\n"
    tweet += "#Finnish #Suomi #LearnFinnish #OpiSuomea"
    return tweet

def post_word_of_the_day():
    word_data = fetch_finnish_word_of_the_day()
    
    if word_data:
        tweet_text = create_tweet_text(word_data)
    else:
        print("All retries failed. Posting fallback tweet.")
        tweet_text = create_fallback_tweet()
    
    print(f"Tweet to post:\n{tweet_text}\n")
    
    try:
        client = get_twitter_client()
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet posted successfully! ID: {response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")
        return False

if __name__ == "__main__":
    post_word_of_the_day()