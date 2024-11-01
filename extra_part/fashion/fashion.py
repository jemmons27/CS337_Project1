import json
import spacy
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

def extract_names(text):
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON'] # and ent in 'Golden Globes' and ent in 'GoldenGlobes']
    #exclude tweets that have "wins" or some variant
    print(names)
    return names

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def process_tweet(tweet):
    #tweet['sentiment'] = analyze_sentiment(tweet['text'])
    tweet['names'] = extract_names(tweet['text'])
    return tweet

with open('./gg2013.json', 'r') as file:
    data = json.load(file)

# Process the tweets
with ThreadPoolExecutor() as executor:
    data = list(executor.map(process_tweet, data))

# Save the cleaned data back to a JSON file
with open('gg2013_sentimented.json', 'w') as file:
    json.dump(data, file, indent=4)