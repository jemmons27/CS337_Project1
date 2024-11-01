import json
import spacy
import re
from collections import Counter

def parse_data(data):
    pattern = r'(?i)\b(fashion|red\s+carpet|best\s+dressed|outfit|clothes?|clothing|style|wardrobe|attire|dress|apparel)\b'
    p = re.compile(pattern)
    res = []
    for tweet in data:
        text = tweet['text']
        if p.search(text):
            res.append(text)
    return res

def clean(data, show):
    pattern = r'(?i)@\w+\b|https?://\S+|#\w+\b|[^a-zA-Z\s]| rt |\b' + re.escape(show) + r'\b|[^\x00-\x7F]+'
    p=re.compile(pattern)
    res = []
    for i in range(len(data)):
        tmp = re.sub(p, '', data[i])
        cleaned_tweet = re.sub(r'\s+', ' ', tmp).strip().lower()
        if cleaned_tweet:
            res.append(cleaned_tweet)
    
    return res

def sentiment(tweets):
    pattern = r'(?i)\b(best|good|love|gorgeous|beautiful|cute|stunning|stuns|wow|pretty|awesome|cool|like)\b'
    p = re.compile(pattern, re.IGNORECASE)
    res = []
    for tweet in tweets:
        if p.search(tweet):
            if tweet:
                res.append(tweet)
    return res

def merge_proper_nouns(doc):
    with doc.retokenize() as retokenizer:
        spans = []
        for i, token in enumerate(doc):
            if token.pos_ == "PROPN" and (i == 0 or doc[i - 1].pos_ == "PROPN"):
                spans.append(token)

            if len(spans) > 1 and (i + 1 >= len(doc) or doc[i + 1].pos_ != "PROPN"):
                retokenizer.merge(doc[spans[0].i: spans[-1].i + 1])
                spans = []
    return doc

        
def main():
    path = 'gg2013.json'
    with open(path, 'r') as file:
        data = json.load(file)
        
    tweets = parse_data(data)
    show = "Golden Globes"
    tweets = clean(tweets, show)
    tweets = sentiment(tweets)
    #bestdressed = fashion(tweets)
if __name__ == '__main__':
    main()