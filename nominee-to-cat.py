import csv
import json
from collections import defaultdict
import re

correct_categories = [
    'best screenplay - motion picture', 'best director - motion picture', 
    'best performance by an actress in a television series - comedy or musical', 
    'best foreign language film', 'best performance by an actor in a supporting role in a motion picture', 
    'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 
    'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 
    'best mini-series or motion picture made for television', 'best original score - motion picture', 
    'best performance by an actress in a television series - drama', 'best performance by an actress in a motion picture - drama', 
    'cecil b. demille award', 'best performance by an actor in a motion picture - comedy or musical', 
    'best motion picture - drama', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television', 
    'best performance by an actress in a supporting role in a motion picture', 'best television series - drama', 
    'best performance by an actor in a mini-series or motion picture made for television', 
    'best performance by an actress in a mini-series or motion picture made for television', 
    'best animated feature film', 'best original song - motion picture', 
    'best performance by an actor in a motion picture - drama', 'best television series - comedy or musical', 
    'best performance by an actor in a television series - drama', 'best performance by an actor in a television series - comedy or musical'
]

def load_nominees(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        nominees = [row[0].strip() for row in reader if row]
    return nominees

def map_nominees_to_categories(tweets, correct_categories, nominees):
    nominee_to_categories = defaultdict(list)
    category_patterns = {category: re.compile(re.escape(category), re.IGNORECASE) for category in correct_categories}
    nominee_patterns = {nominee: re.compile(re.escape(nominee), re.IGNORECASE) for nominee in nominees}

    for tweet in tweets:
        text = tweet.get("text", "")

        for nominee, nominee_pattern in nominee_patterns.items():
            if len(nominee) > 4 and nominee_pattern.search(text):
                for category, category_pattern in category_patterns.items():
                    if category_pattern.search(text):
                        if nominee not in nominee_to_categories[category] and "nominee" not in nominee:
                            nominee_to_categories[category].append(nominee)
    
    return dict(nominee_to_categories)

# Example usage:
tweets_file_path = "/Users/jasminemeyer/CS337_Project1/gg2013.json"
nominees_file_path = "/Users/jasminemeyer/CS337_Project1/df/nominees.csv"

# Load data
with open(tweets_file_path, 'r') as file:
    tweets = json.load(file)

nominees = load_nominees(nominees_file_path)

# Map nominees to categories
nominee_to_categories = map_nominees_to_categories(tweets, correct_categories, nominees)
# Print each item with a newline in between
for category, nominees in nominee_to_categories.items():
    print(f"{category}: {nominees}\n")