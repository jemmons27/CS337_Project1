import json
import spacy
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

# Define a list of party-related keywords
party_keywords = ['party', 'after-party', 'afterparty', 'celebration', 'gala']

def extract_parties(text):
    doc = nlp(text)
    parties = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'EVENT'] and any(keyword in ent.text.lower() for keyword in party_keywords)]
    return parties

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def process_tweets(tweets):
    texts = [tweet['text'] for tweet in tweets]
    docs = list(nlp.pipe(texts, batch_size=50))
    for tweet, doc in zip(tweets, docs):
        parties = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'EVENT'] and any(keyword in ent.text.lower() for keyword in party_keywords)]
        if parties:
            tweet['parties'] = parties
            tweet['sentiment'] = analyze_sentiment(tweet['text'])
    return tweets

# Load the JSON data from the file
with open('/Users/jasminemeyer/CS337_Project1/gg2013.json', 'r') as file:
    data = json.load(file)

# Process the tweets in parallel
batch_size = 100
processed_data = []
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_tweets, data[i:i + batch_size]) for i in range(0, len(data), batch_size)]
    for future in as_completed(futures):
        processed_data.extend(future.result())

# Count party mentions and aggregate sentiment
party_counter = Counter()
party_sentiment = defaultdict(list)

for tweet in processed_data:
    if 'parties' in tweet:
        for party in tweet['parties']:
            party_counter[party] += 1
            party_sentiment[party].append(tweet['sentiment'])

# Calculate average sentiment for each party
party_avg_sentiment = {party: sum(sentiments) / len(sentiments) for party, sentiments in party_sentiment.items()}

# Save the results to a JSON file
results = {
    'party_mentions': party_counter,
    'party_avg_sentiment': party_avg_sentiment
}

with open('/Users/jasminemeyer/CS337_Project1/party_analysis_results.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Party analysis results saved to party_analysis_results.json")