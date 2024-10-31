import json
import re
import spacy
from rapidfuzz import process, fuzz  # Using RapidFuzz for matching
import csv

nlp = spacy.load('en_core_web_sm')

# Define the condensed presenter regex pattern
presenter_pattern = r"([A-Za-z\s&]+?)\s+(?:is\s+presenting|to\s+present|presented|gives?\s+out|gave|is\s+announcing|announced|reveal(?:s|ed)?|hands?\s+(?:over|out)|unveil(?:s|ed)?|introduces?\s+nominees\s+for|just\s+presented|hosts?|awarding|brings?\s+out|steps\s+up\s+to\s+present|announces?\s+winner\s+of|presenting)\s+(?:the\s+)?(Best\s.+?)\b"

# Compile the regex pattern with case-insensitive flag
compiled_presenter_pattern = re.compile(presenter_pattern, re.IGNORECASE)

def extract_presenters_and_awards(file_path):
    """
    Extracts potential presenters and their associated awards from tweets in the given file path,
    capturing the full award name starting with 'Best'.

    Args:
        file_path (str): Path to the JSON file containing tweets.

    Returns:
        list[dict]: List of dictionaries with 'presenter' and 'award' keys.
    """
    # Load tweets from the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

    presenter_award_pairs = []

    for tweet in data:
        tweet_text = tweet.get('text', '')
        if not tweet_text:
            continue  # Skip tweets without text

        # Apply the compiled regex pattern to the tweet text
        matches = compiled_presenter_pattern.findall(tweet_text)
        for match in matches:
            # Initialize presenters and awards lists
            presenters = []
            awards = []

            # Extract presenter and award parts from the match
            if 'presented by' in compiled_presenter_pattern.pattern or 'goes to' in compiled_presenter_pattern.pattern:
                # Patterns like "[Award] presented by [Entity]" or "[Award] goes to [Recipient], presented by [Entity]"
                # Not applicable here since we have a single pattern capturing (presenter, award)
                presenter_part = match[0]
                award_part = match[1]
            elif 'and' in compiled_presenter_pattern.pattern and len(match) == 3:
                # Patterns with two presenters - Not applicable here since we have a single pattern
                presenter_part = f"{match[0]} and {match[1]}"
                award_part = match[2]
            else:
                presenter_part = match[0]
                award_part = match[1]

            # Clean the award_part
            award_part = award_part.strip(' .,!?')

            # Use SpaCy to identify PERSON entities in the presenter_part
            doc_entities = nlp(presenter_part)
            for ent in doc_entities.ents:
                if ent.label_ == 'PERSON':
                    presenter_name = ent.text.strip()
                    # Handle multiple presenters connected by 'and' or '&'
                    individual_presenters = re.split(r'\band\b|&', presenter_name)
                    for p in individual_presenters:
                        p = p.strip()
                        if p:
                            presenters.append(p)

            # Only proceed if we have at least one presenter
            if not presenters:
                continue

            # Combine presenters and awards into pairs
            for presenter in presenters:
                presenter_award_pairs.append({'presenter': presenter, 'award': award_part})

    # Remove duplicates by converting the list of dictionaries to a set of tuples
    unique_pairs = [dict(t) for t in {tuple(d.items()) for d in presenter_award_pairs}]

    print("\nList of presenter-award pairs before matching:")
    for pair in unique_pairs:
        print(f"Presenter: {pair['presenter']} - Award: {pair['award']}")

    return unique_pairs

def match_awards(unique_pairs, known_awards, threshold=80):
    """
    Matches extracted award names to the closest known awards using fuzzy matching.

    Args:
        unique_pairs (list[dict]): List of dictionaries with 'presenter' and 'award' keys.
        known_awards (list[str]): List of standardized award names.
        threshold (int): Minimum similarity score to consider a match valid.

    Returns:
        list[dict]: List of dictionaries with 'presenter' and 'matched_award' keys.
    """
    matched_pairs = []

    for pair in unique_pairs:
        award = pair['award']
        # Use RapidFuzz's process.extractOne to find the best match
        match, score, _ = process.extractOne(
            award, known_awards, scorer=fuzz.WRatio
        )
        if score >= threshold:
            matched_award = match
        else:
            matched_award = award  # If no good match found, keep the original

        matched_pairs.append({
            'presenter': pair['presenter'],
            'matched_award': matched_award
        })

    return matched_pairs