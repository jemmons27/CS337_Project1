import json
import re
import spacy

nlp = spacy.load('en_core_web_sm')

presenter_patterns = [
    # Pattern for "[Entity] is presenting [award]"
    r"([A-Za-z\s&]+?)\s+is\s+presenting\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] to present [award]"
    r"([A-Za-z\s&]+?)\s+to\s+present\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] presented [award]"
    r"([A-Za-z\s&]+?)\s+presented\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Award] presented by [Entity]"
    r"(Best\s.*?)(?=[.,!?]|$)\s+presented\s+by\s+([A-Za-z\s&]+?)\b",
    
    # Pattern for "[Entity] gives out [award]"
    r"([A-Za-z\s&]+?)\s+gives\s+out\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] gave [award]"
    r"([A-Za-z\s&]+?)\s+gave\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] is announcing [award]"
    r"([A-Za-z\s&]+?)\s+is\s+announcing\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] announced [award]"
    r"([A-Za-z\s&]+?)\s+announced\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] reveals [award]" and "[Entity] revealed [award]"
    r"([A-Za-z\s&]+?)\s+reveal(?:s|ed)?\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] hands over [award]" and "[Entity] hands out [award]"
    r"([A-Za-z\s&]+?)\s+hands?\s+(?:over|out)\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] unveils [award]"
    r"([A-Za-z\s&]+?)\s+unveil(?:s|ed)?\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] introduces nominees for [award]"
    r"([A-Za-z\s&]+?)\s+introduces?\s+nominees\s+for\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] presenting [award]"
    r"([A-Za-z\s&]+?)\s+presenting\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Award] goes to [Recipient], presented by [Entity]"
    r"(Best\s.*?)(?=[.,!?]|$)\s+goes\s+to\s+.+?,\s+presented\s+by\s+([A-Za-z\s&]+?)\b",
    
    # Pattern for "[Entity] on stage to present [award]"
    r"([A-Za-z\s&]+?)\s+on\s+stage\s+to\s+present\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] announces winner of [award]"
    r"([A-Za-z\s&]+?)\s+announces?\s+winner\s+of\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] just presented [award]"
    r"([A-Za-z\s&]+?)\s+just\s+presented\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] and [Entity] present [award]"
    r"([A-Za-z\s&]+?)\s+and\s+([A-Za-z\s&]+?)\s+present\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] hosts [award] segment"
    r"([A-Za-z\s&]+?)\s+hosts?\s+(Best\s.*?)(?=[.,!?]|$)\s+segment\b",
    
    # Pattern for "[Entity] steps up to present [award]"
    r"([A-Za-z\s&]+?)\s+steps\s+up\s+to\s+present\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] awarding [award]"
    r"([A-Za-z\s&]+?)\s+awarding\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] brings out [award]"
    r"([A-Za-z\s&]+?)\s+brings?\s+out\s+(Best\s.*?)(?=[.,!?]|$)",
    
    # Pattern for "[Entity] gives [award] to [Recipient]"
    r"([A-Za-z\s&]+?)\s+gives?\s+(Best\s.*?)(?=[.,!?]|$)\s+to\s+.+?\b",
]

compiled_presenter_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in presenter_patterns]

def extract_presenters_and_awards(file_path):
    """
    Extracts potential presenters and their associated awards from tweets in the given file path,
    capturing the full award name starting with 'Best'.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    presenter_award_pairs = []

    for tweet in data:
        tweet_text = tweet.get('text', '')
        if not tweet_text:
            continue

        # Apply each compiled regex pattern to the tweet text
        for pattern in compiled_presenter_patterns:
            matches = pattern.findall(tweet_text)
            for match in matches:
                # Initialize presenters and awards lists
                presenters = []
                awards = []

                # Handle patterns with different group structures
                if 'presented by' in pattern.pattern or 'goes to' in pattern.pattern:
                    # Patterns like "[Award] presented by [Entity]" or "[Award] goes to [Recipient], presented by [Entity]"
                    award_part, entity_part = match
                elif 'and' in pattern.pattern and len(match) == 3:
                    # Patterns with two presenters
                    entity_part = f"{match[0]} and {match[1]}"
                    award_part = match[2]
                else:
                    entity_part, award_part = match

                # Clean the award_part
                award_part = award_part.strip(' .,!?')

                # Use SpaCy to identify PERSON entities in the entity_part
                doc_entities = nlp(entity_part)
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

    print("\nList of presenter-award pairs:")
    for pair in unique_pairs:
        print(f"Presenter: {pair['presenter']} - Award: {pair['award']}")

    return unique_pairs

file_path = 'gg2013.json'  
extract_presenters_and_awards(file_path)
