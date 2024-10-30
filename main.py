import re
import json
import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
                
def award_categories_answers(file_path_answers):
    award_categories_answers = []
    with open(file_path_answers, 'r') as file:
        data = json.load(file)
    for i in data["award_data"]:
        award_categories_answers.append(i)
    return award_categories_answers

def nominees_answers(file_path_answers):
    nominees = []
    with open(file_path_answers, 'r') as file:
        data = json.load(file)
    for key,val in data["award_data"].items():
        
        nominees.extend(val["nominees"])
        nominees.append(val["winner"])
    print(nominees)


def parse_json(file_path, file_path_answers):
    nlp = spacy.load("en_core_web_sm")
    with open(file_path, 'r') as file:
        data = json.load(file)
    with open(file_path_answers, 'r') as file:
        data_answers = json.load(file)
    nominees = ["zero dark thirty", "lincoln", "silver linings playbook", "argo", "django unchained"]
    
    result = ''
    regex = r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+[\w\s]+)"
    categories = award_categories_answers("/Users/mahimaramesh/CS337_Project1/gg2013answers.json")
    
   
    for item in data:
        
        match = re.findall(regex, item["text"])
        if match:
            
            

            for i in match:
                person = i[0]
                        
                query = i[2]
                potential_matches = process.extract(query, categories, limit=15)
                split = query.split(" ")
                
                filtered_matches = [
    match for match, score in potential_matches
    if all(word in match.lower() for word in split)]
                print(person, filtered_matches)
                
                
            
                for i in filtered_matches:
                    nominees = []
                    nominees.extend(data_answers["award_data"][i]["nominees"])
                    nominees.append(data_answers["award_data"][i]["winner"])
                    person = person.lower()
                    if person in nominees:
                        
                        print(person, i)




            
            # for token in match:
            #     # Normalize the token text to lowercase for comparison
            #     normalized_token = token.text.lower()
            #     if normalized_token in nominees:
            #         result += f"Match found: {normalized_token}\n"
            #         print(f"Match found: {normalized_token}")  # Optional: print to console


    
    


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





print(parse_json("/Users/mahimaramesh/CS337_Project1/gg2013.json", "/Users/mahimaramesh/CS337_Project1/gg2013answers.json"))








