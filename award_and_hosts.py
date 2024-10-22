import json
import re
from collections import Counter
import wordninja
import spacy

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
    Cleans and normalizes text by converting to lowercase
    and stripping whitespace.
    """
    text = text.lower()
    return text.strip()

def find_award_name(tweets):
    """
    Finds the award show name by extracting the most common hashtag
    and splitting it into words.
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

        # Split the hashtag into words using wordninja
        words = wordninja.split(most_common_hashtag)
        # Capitalize each word to form the award show name
        award_name = ' '.join(word.capitalize() for word in words)
        print(f"The award show name is: {award_name}")
        return award_name
    else:
        print("No hashtags found.")
        return None

def find_hosts(tweets, award_name):
    """
    Finds the hosts' names by applying regex patterns and SpaCy NER to the tweets.
    Excludes names that match the award show name.
    Only considers tweets that match the hosting regex patterns.
    Returns the top 5 most mentioned host names.
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

    # List to store potential host names
    potential_hosts = []

    # Normalize the award show name for comparison
    normalized_award_name = clean_text(award_name.replace(' ', ''))

    for tweet in tweets:
        # Flag to indicate if the tweet matches any host pattern
        matches_host_pattern = False

        # Apply regex patterns to the tweet
        for pattern in compiled_patterns:
            matches = pattern.findall(tweet)
            if matches:
                matches_host_pattern = True
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
                            # Exclude single-word names and award show name
                            if host and len(host.split()) >= 2:
                                if normalized_award_name not in clean_text(host).replace(' ', ''):
                                    potential_hosts.append(host)

        # If the tweet matches any host pattern, proceed to extract PERSON entities
        if matches_host_pattern:
            doc = nlp(tweet)
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    host_name = clean_text(ent.text)
                    host_name = ' '.join(host_name.split())
                    # Exclude single-word names and award show name
                    if host_name and len(host_name.split()) >= 2:
                        # Exclude if host_name contains award show name
                        if normalized_award_name not in clean_text(host_name).replace(' ', ''):
                            # Dependency parsing: check if host_name is subject or object of hosting verb
                            token = ent.root
                            if (token.head.lemma_ in ['host', 'hosting', 'hosted', 'kick', 'kick off'] 
                                and token.head.pos_ == 'VERB'
                                and token.dep_ in ['nsubj', 'dobj']):
                                potential_hosts.append(host_name)

    # Count the frequency of each potential host name
    host_name_counts = Counter(potential_hosts)

    # Identify the top 5 most common host names
    if host_name_counts:
        most_common_hosts = host_name_counts.most_common(5)
        print("\nTop 5 most likely host(s):")
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
    tweets = [item.get('text', '') for item in data]

    # Find the award name
    award_name = find_award_name(tweets)

    if award_name:
        # Find the hosts
        find_hosts(tweets, award_name)
    else:
        print("Could not determine the award show name.")

if __name__ == "__main__":
    main()
