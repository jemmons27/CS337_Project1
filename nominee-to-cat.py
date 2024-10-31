import csv
import json
from collections import defaultdict
import re

def load_award_categories(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Convert the list of lists into a dictionary with categories as keys
    award_categories = {item[0].strip(): item[1] for item in data}
    return award_categories

def load_nominees(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        nominees = [row[0].strip() for row in reader if row]
    return nominees

def map_nominees_to_categories(tweets, award_categories, nominees):
    nominee_to_categories = defaultdict(list)
    category_patterns = {category: re.compile(re.escape(category), re.IGNORECASE) for category in award_categories.keys()}
    nominee_patterns = {nominee: re.compile(re.escape(nominee), re.IGNORECASE) for nominee in nominees}

    for tweet in tweets:
        text = tweet.get("text", "")
        for nominee, nominee_pattern in nominee_patterns.items():
            if nominee_pattern.search(text):
                for category, category_pattern in category_patterns.items():
                    if category_pattern.search(text):
                        if nominee not in nominee_to_categories[category]:
                            nominee_to_categories[category].append(nominee)
    
    return dict(nominee_to_categories)

# Example usage:
tweets_file_path = "/Users/jasminemeyer/CS337_Project1/gg2013.json"
award_categories_file_path = "/Users/jasminemeyer/CS337_Project1/categories.json"
nominees_file_path = "/Users/jasminemeyer/CS337_Project1/df/nominees.csv"

# Load data
with open(tweets_file_path, 'r') as file:
    tweets = json.load(file)

award_categories = load_award_categories(award_categories_file_path)
nominees = load_nominees(nominees_file_path)

# Map nominees to categories
nominee_to_categories = map_nominees_to_categories(tweets, award_categories, nominees)
# Print each item with a newline in between
for nominee, categories in nominee_to_categories.items():
    print(f"{nominee}: {categories}\n")