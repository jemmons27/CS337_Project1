import json
from ftfy import fix_text
import unidecode
import spacy
def nominees(input):
    model = spacy.load('en_core_web_sm')
    with open(input, 'r') as file:
        data=json.load(file)
    res = []
    for tweet in data:
        cleaned = unidecode.unidecode_expect_nonascii(tweet['text'])
        cleaned = fix_text(cleaned)
        cleaned = " ".join(cleaned.split())
        output = model(cleaned)
        for entity in output.ents:
            if entity.label_ == 'PERSON':
                if entity.text not in res:
                    res.append(entity.text)
    print(res)
    
nominees('gg2013.json')