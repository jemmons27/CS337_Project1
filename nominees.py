import json
from ftfy import fix_text
import unidecode
import spacy
import re
from collections import Counter

def clean_text(text):
    """
    Cleans and normalizes text by converting to lowercase and stripping whitespace.
    """
    return text.lower().strip()

def nominees(input):
    nom_regex = [r"([A-Za-z\s]+)\s+loses\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+was\s+nominated\s+for\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+deserved\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+didn't\s+get\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+should\s+have\s+won\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+was\s+robbed",
          r"([A-Za-z\s]+)\s+got\s+robbed",
          r"([A-Za-z\s]+)\s+lost"]
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in nom_regex]
    
    model = spacy.load('en_core_web_sm')
    with open(input, 'r') as file:
        data=json.load(file)
    res = []
    for tweet in data:
        #cleaned = unidecode.unidecode_expect_nonascii(tweet['text']) #emojis
        #cleaned = fix_text(cleaned) #&AMP -> &
        #cleaned = " ".join(cleaned.split()) #Extra White Space
        #output = model(cleaned)
        body = tweet['text']
        has_pattern = False
        for pattern in compiled_patterns:
            if pattern.search(body):
                has_pattern = True
                break
        if has_pattern:
            for pattern in compiled_patterns:
                matches=pattern.findall(body)
            
                if matches == []:
                    continue
                elif isinstance(matches[0], tuple):
                    matches = ' '.join(matches[0])
                else:
                    #print(matches)
                    nominee = clean_text(matches[0])
                    nominee = ' '.join(nominee.split())
                    output = model(nominee)
                    for chunk in output.noun_chunks:
                        res.append(chunk.text)
    res_count = Counter(res)        
    print(res_count)
    
nominees('gg2013.json')

'''
Grab nominees, award names, hosts, presenters hopefully in one pass

Separate into nominees and their respective tweets

Using these two, tally up for mentions next to awards
'''