import re
import json
import spacy
from cydifflib import SequenceMatcher
import difflib
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from collections import Counter

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
    regex = r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+[\w\s]+)"
    categories = award_categories_answers("/Users/mahimaramesh/CS337_Project1/gg2013answers.json")
    answers = {}
   
    for item in data:
        
        match = re.findall(regex, item["text"])
        if match:
            for i in match:
                person = i[0]
                        
                query = i[2]
                maxAward = []
                maxSeq = 0
                for award in categories:
                    seq = difflib.SequenceMatcher(a=i[2].lower(), b=award.lower())
                    if seq.ratio() > maxSeq:
                        maxAward.append(award)
                        maxSeq = seq.ratio()
                    elif seq.ratio() == maxSeq:
                        maxAward.append(award)
                if len(maxAward) > 1:
                    query_words = set(query.lower().split())
                    maxAward = max(maxAward, key=lambda award: len(query_words.intersection(award.lower().split())))

                    if answers.get(maxAward) == None:
                        answers[maxAward] = []
                    answers[maxAward].append(person)
    
    top_mentions = {}
    for award, people in answers.items():
        # Count occurrences of each person
        person_counts = Counter(people)
        # Get the top 3 most common people
        top_mentions[award] = [person for person, count in person_counts.most_common(3)]

    print(Counter(answers["best television series - drama"]))
                

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








