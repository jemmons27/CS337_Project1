import re
import json
import spacy

#preprocess data and most hashtags = award show

def entities(file):
    with open(file, 'r') as ggs:
        nlp = spacy.load("en_core_web_sm")
        data = json.load(ggs)
        for i in data:
            ent = nlp(i['text'])
            co = 0
            for j in ent.ents:
                print(j.text, j.label_)
                co += 1
                if co == 10:
                    return

def parse_json(file_path):
    nlp = spacy.load("en_core_web_sm")
    with open(file_path, 'r') as file:
        data = json.load(file)
    nominees = ["zero dark thirty", "lincoln", "silver linings playbook", "argo", "django unchained"]
    
    result = ''
    regex = r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+\w+(?:\s\w+)*)"
    for item in data:
        match = re.findall(regex, item["text"])
        if match:
            #doc = nlp(match[0][0])
            for token in match:
                # Normalize the token text to lowercase for comparison
                normalized_token = token.text.lower()
                if normalized_token in nominees:
                    result += f"Match found: {normalized_token}\n"
                    print(f"Match found: {normalized_token}")  # Optional: print to console


    
    return result


def regex_splitting(string, regex):
    match = re.findall(regex, string)
    actor = match[0]
    award = match[1]

def all_candidate_strings(award):
    current_string = ""
    result = []
    words = award.split(" ")
    for i in words:
        current_string = current_string + i + " "
        result.append(current_string)
    return result

def find_winners(nominees, award_name):
    entity_pattern = r'(\w+(?: \w+)*)'
    award_name = "Best Actor"
    regex_pattern = rf'{entity_pattern} wins ({award_name})'





print(parse_json("/Users/mahimaramesh/CS337_Project1/gg2013.json"))







