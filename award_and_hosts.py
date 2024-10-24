import json
import re
from collections import Counter
import wordninja
import spacy
from datetime import datetime, timedelta

# Load the SpaCy English model for NER
nlp = spacy.load("en_core_web_sm")

def load_json(file_path):
    """
    Loads JSON data from the given file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def clean_text(text):
    """
    Cleans and normalizes text by converting to lowercase and stripping whitespace.
    """
    return text.lower().strip()

def find_award_name(tweets):
    """
    Finds the award show name by extracting the most common hashtag and splitting it into words.
    Uses all tweets without time filtering.
    """
    hashtags = []
    hashtag_pattern = re.compile(r"#(\w+)", re.IGNORECASE)

    for tweet in tweets:
        found_hashtags = hashtag_pattern.findall(tweet)
        for tag in found_hashtags:
            hashtag_text = clean_text(tag)
            if hashtag_text:
                hashtags.append(hashtag_text)

    hashtag_counts = Counter(hashtags)

    if hashtag_counts:
        most_common_hashtag, count = hashtag_counts.most_common(1)[0]
        print(f"The most mentioned hashtag is: #{most_common_hashtag}")
        print(f"Number of mentions: {count}")

        # Split the hashtag into words
        words = wordninja.split(most_common_hashtag)
        # Capitalize each word
        award_name = ' '.join(word.capitalize() for word in words)
        print(f"The award show name is: {award_name}")
        return award_name
    else:
        print("No hashtags found.")
        return None

def find_hosts(tweets, award_name, earliest_time):
    """
    Finds the hosts' names by applying regex patterns and SpaCy NER to the tweets.
    Only considers tweets that match the hosting regex patterns.
    Then filters these tweets to those within the first 30 minutes from earliest_time.
    Excludes any names that match or contain the award show name.
    Returns the top 2 most common host names.
    """
    # Regex patterns provided
    host_patterns = [
        r"([A-Za-z\s]+)\s+hosts?\b",
        r"([A-Za-z\s]+)\.\.\.\s*hosting\b",
        r"([A-Za-z\s]+)\s+kicks\s+off\b",
        r"Hosts?\s+([A-Za-z\s]+)",
        r"([A-Za-z\s]+)\s+hosted\b",
        r"hosted by\s+([A-Za-z\s]+)\b"
    ]

    # Compile regex patterns
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in host_patterns]

    # Normalize the award show name for comparison
    normalized_award_name = clean_text(award_name.replace(' ', ''))

    # Define the time window (first 30 minutes from earliest_time)
    time_window = earliest_time + timedelta(minutes=30)

    # List to store potential host names
    potential_hosts = []

    for tweet_data in tweets:
        tweet_text = tweet_data.get('text', '')
        timestamp_ms = tweet_data.get('timestamp_ms', '')
        if not tweet_text or not timestamp_ms:
            continue  # Skip if text or timestamp is missing

        # Parse the timestamp
        timestamp = datetime.fromtimestamp(int(timestamp_ms)/1000)

        # Apply regex patterns to check if the tweet is about hosting
        matches_host_pattern = False
        for pattern in compiled_patterns:
            if pattern.search(tweet_text):
                matches_host_pattern = True
                break

        if matches_host_pattern:
            # Check if the tweet is within the time window
            if timestamp <= time_window:
                # Apply regex patterns to extract host names
                for pattern in compiled_patterns:
                    matches = pattern.findall(tweet_text)
                    for match in matches:
                        # Ensure match is a string (handles groups)
                        if isinstance(match, tuple):
                            match = ' '.join(match)
                        # Clean and normalize the host name
                        host_name = clean_text(match)
                        # Remove extra spaces and ensure it's not empty
                        host_name = ' '.join(host_name.split())
                        if host_name:
                            # Split names if 'and' or '&' is used
                            individual_hosts = re.split(r'\band\b|&', host_name)
                            for host in individual_hosts:
                                host = host.strip()
                                if host:
                                    # Exclude if host name contains award show name
                                    if normalized_award_name not in host.replace(' ', ''):
                                        potential_hosts.append(host)
                # Use SpaCy NER to extract person names
                doc = nlp(tweet_text)
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        host_name = clean_text(ent.text)
                        host_name = ' '.join(host_name.split())
                        if host_name:
                            # Exclude if host name contains award show name
                            if normalized_award_name not in host_name.replace(' ', ''):
                                potential_hosts.append(host_name)

    # Count the frequency of each potential host name
    host_name_counts = Counter(potential_hosts)

    # Identify the top 2 most common host names
    if host_name_counts:
        most_common_hosts = host_name_counts.most_common(2)
        print("\nTop 2 most likely host(s):")
        for host, count in most_common_hosts:
            # Capitalize each word in the host name
            host_name_formatted = ' '.join(word.capitalize() for word in host.split())
            print(f"- {host_name_formatted}: mentioned {count} times")
    else:
        print("\nNo host names found.")

def main():
    # Set the file path to your JSON data
    file_path = 'gg2013.json'

    # Load tweets from the JSON file
    data = load_json(file_path)

    # Extract tweets' text for award name finding
    tweets_text = [item.get('text', '') for item in data if 'text' in item]

    # Find the award name using all tweets
    award_name = find_award_name(tweets_text)

    if not award_name:
        print("Could not determine the award show name.")
        return

    # Extract timestamps to find the earliest timestamp
    timestamps = []
    for item in data:
        timestamp_ms = item.get('timestamp_ms', '')
        if timestamp_ms:
            timestamp = datetime.fromtimestamp(int(timestamp_ms)/1000)
            timestamps.append(timestamp)
    if not timestamps:
        print("No valid timestamps found.")
        return

    earliest_time = min(timestamps)

    # Find the hosts using filtered tweets
    find_hosts(data, award_name, earliest_time)

if __name__ == "__main__":
    main()
