import requests
import tweepy
import os
import time
import random
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# URL to the KOTUS Finnish word list
WORD_LIST_URL = "https://raw.githubusercontent.com/hugovk/everyfinnishword/master/kaikkisanat.txt"

def get_twitter_client():
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )
    return client

def fetch_word_list(max_retries=3):
    """Fetch the Finnish word list from GitHub"""
    for attempt in range(max_retries):
        try:
            response = requests.get(WORD_LIST_URL, timeout=30)
            if response.status_code == 200:
                words = response.text.strip().split('\n')
                # Filter out empty lines and very short words
                words = [w.strip() for w in words if len(w.strip()) >= 3]
                return words
            else:
                print(f"Attempt {attempt + 1}: Failed to fetch word list, status {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed - {e}")
        
        if attempt < max_retries - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)
    
    return None

def get_daily_word(words):
    """Select a consistent word for the day based on the date"""
    today = datetime.now().strftime("%Y-%m-%d")
    seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
    random.seed(seed)
    return random.choice(words)

def create_tweet_text(word):
    """Create the tweet text"""
    tweet = f"🇫🇮 Päivän Sana / Finnish Word of the Day\n\n"
    tweet += f"✨ {word} ✨\n\n"
    tweet += f"📖 Tarkista määritelmä täältä: https://www.suomisanakirja.fi/{word}\n\n"
    tweet += f"🤔 Osaatko käyttää tätä sanaa lauseessa? Can you use this word in a sentence?\n\n"
    tweet += "#Finnish #Suomi #LearnFinnish #OpiSuomea"
    
    if len(tweet) > 280:
        # If too long, shorten the interactive question
        tweet = f"🇫🇮 Päivän Sana / Finnish Word of the Day\n\n"
        tweet += f"✨ {word} ✨\n\n"
        tweet += f"📖 https://www.suomisanakirja.fi/{word}\n\n"
        tweet += "#Finnish #Suomi #LearnFinnish #OpiSuomea"
    
    return tweet

def create_fallback_tweet():
    """Fallback tweet if everything fails"""
    tweet = "🇫🇮 Päivän Sana / Finnish Word of the Day\n\n"
    tweet += "😢 Ei sanaa tänään / No word today\n\n"
    tweet += "Tarkista huomenna uudelleen!\nCheck back tomorrow!\n\n"
    tweet += "#Finnish #Suomi #LearnFinnish #OpiSuomea"
    return tweet

def post_word_of_the_day():
    """Main function to fetch and tweet the word"""
    words = fetch_word_list()
    
    if not words:
        print("Failed to fetch word list. Posting fallback tweet.")
        tweet_text = create_fallback_tweet()
    else:
        print(f"Loaded {len(words)} Finnish words")
        
        word = get_daily_word(words)
        print(f"Today's word: {word}")
        
        tweet_text = create_tweet_text(word)
    
    print(f"\nTweet to post:\n{tweet_text}\n")
    
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