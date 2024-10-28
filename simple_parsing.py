import json

def parse_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    result = ''
    for item in data:
        if 'text' in item and 'Best' in item['text']:
            result += '>' + item['text'] + '\n'
    
    return result


file_path = '/Users/jasminemeyer/Downloads/gg2013.json'
print(parse_json(file_path))