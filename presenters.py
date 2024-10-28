import json
import re
import spacy

# Load the SpaCy English model for NER
nlp = spacy.load('en_core_web_sm')

# Define the expressions and create regex patterns
presenter_patterns = [
    # Pattern for "[Entity] is presenting [award]"
    r"([A-Za-z\s&]+?)\s+is\s+presenting\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] to present [award]"
    r"([A-Za-z\s&]+?)\s+to\s+present\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] presented [award]"
    r"([A-Za-z\s&]+?)\s+presented\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Award] presented by [Entity]"
    r"(?:the\s+)?(.+?)\s+presented\s+by\s+([A-Za-z\s&]+?)\b",

    # Pattern for "[Entity] gives out [award]"
    r"([A-Za-z\s&]+?)\s+gives\s+out\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] gave [award]"
    r"([A-Za-z\s&]+?)\s+gave\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] is announcing [award]"
    r"([A-Za-z\s&]+?)\s+is\s+announcing\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] announced [award]"
    r"([A-Za-z\s&]+?)\s+announced\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] reveals [award]" and "[Entity] revealed [award]"
    r"([A-Za-z\s&]+?)\s+reveal(?:s|ed)?\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] hands over [award]" and "[Entity] hands out [award]"
    r"([A-Za-z\s&]+?)\s+hands?\s+(?:over|out)\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] unveils [award]"
    r"([A-Za-z\s&]+?)\s+unveil(?:s|ed)?\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] introduces nominees for [award]"
    r"([A-Za-z\s&]+?)\s+introduces?\s+nominees\s+for\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] presenting [award]"
    r"([A-Za-z\s&]+?)\s+presenting\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Award] goes to [Recipient], presented by [Entity]"
    r"(?:the\s+)?(.+?)\s+goes\s+to\s+(.+?),\s+presented\s+by\s+([A-Za-z\s&]+?)\b",

    # Pattern for "[Entity] on stage to present [award]"
    r"([A-Za-z\s&]+?)\s+on\s+stage\s+to\s+present\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] announces winner of [award]"
    r"([A-Za-z\s&]+?)\s+announces?\s+winner\s+of\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] just presented [award]"
    r"([A-Za-z\s&]+?)\s+just\s+presented\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] and [Entity] present [award]"
    r"([A-Za-z\s&]+?)\s+and\s+([A-Za-z\s&]+?)\s+present\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] hosts [award] segment"
    r"([A-Za-z\s&]+?)\s+hosts?\s+(?:the\s+)?(.+?)\s+segment\b",

    # Pattern for "[Entity] steps up to present [award]"
    r"([A-Za-z\s&]+?)\s+steps\s+up\s+to\s+present\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] awarding [award]"
    r"([A-Za-z\s&]+?)\s+awarding\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] brings out [award]"
    r"([A-Za-z\s&]+?)\s+brings?\s+out\s+(?:the\s+)?(.+?)\b",

    # Pattern for "[Entity] gives [award] to [Recipient]"
    r"([A-Za-z\s&]+?)\s+gives?\s+(?:the\s+)?(.+?)\s+to\s+([A-Za-z\s&]+?)\b",
]

# Compile the regex patterns with case-insensitive flag
compiled_presenter_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in presenter_patterns]

def extract_presenters(file_path):
    """
    Extracts potential presenters from tweets in the given file path.
    """
    # Load tweets from the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    potential_presenters = []

    for tweet in data:
        tweet_text = tweet.get('text', '')
        if not tweet_text:
            continue

        # Apply each compiled regex pattern to the tweet text
        for pattern in compiled_presenter_patterns:
            matches = pattern.findall(tweet_text)
            for match in matches:
                # Depending on the pattern, match may have different lengths
                if len(match) == 2:
                    entity_part, _ = match
                elif len(match) == 3:
                    # Handle patterns with two entities (e.g., presenters connected by 'and')
                    if 'and' in pattern.pattern:
                        entity_part = f"{match[0]} and {match[1]}"
                    else:
                        entity_part = match[0]
                else:
                    continue  # Skip if the match doesn't fit expected patterns

                # Use SpaCy to identify PERSON entities in the entity_part
                doc = nlp(entity_part)
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        presenter_name = ent.text.strip()
                        # Handle multiple presenters connected by 'and' or '&'
                        individual_presenters = re.split(r'\band\b|&', presenter_name)
                        for p in individual_presenters:
                            p = p.strip()
                            if p:
                                potential_presenters.append(p)

    # Remove duplicates by converting to a set, then back to a list
    unique_presenters = list(set(potential_presenters))

    print("\nList of potential presenters:")
    for presenter in unique_presenters:
        print(presenter)

    return unique_presenters

file_path = 'gg2013.json'
extract_presenters(file_path)
