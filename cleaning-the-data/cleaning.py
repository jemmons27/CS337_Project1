import json
import nltk
from nltk.tokenize import word_tokenize

#necessary NLTK data files
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(nltk.corpus.stopwords.words('english'))

# Load the JSON data from the file
with open('/Users/jasminemeyer/CS337_Project1/gg2013.json', 'r') as file:
    data = json.load(file)

# Function to clean each entry
def clean_entry(entry):
    # Remove URLs from the text
    entry['text'] = ' '.join(word for word in entry['text'].split() if not word.startswith('http'))
    # Remove hashtags from the text
    entry['text'] = ' '.join(word for word in entry['text'].split() if not word.startswith('#'))
    #normalizing text to lowercase
    entry['text'] = entry['text'].lower()
    #tokenizing the text
    tokenized_text = word_tokenize(entry['text'])
    #removing stopwords
    tokenized_text = [word for word in tokenized_text if word not in stop_words]
    #simplifying the data
    return {
        'text': tokenized_text,
        'user_id': entry['user']['id']
    }

# Clean the data
cleaned_data = [clean_entry(entry) for entry in data]

# Save the cleaned data back to a JSON file
with open('gg2013_cleaned.json', 'w') as file:
    json.dump(cleaned_data, file, indent=4) 