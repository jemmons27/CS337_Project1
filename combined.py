import numpy as np
import json
from langdetect import detect, detect_langs
import re
import pandas as pd
import time
from datetime import datetime, timedelta
import spacy
import wordninja
from collections import Counter
from os import mkdir
from fuzzywuzzy import fuzz

from warnings import simplefilter 


def extract_data(path):
    '''
    extract_data(path: str) -> json
    Opens file at path and returns its data
    Expects .json files
    '''
    with open(path, 'r') as f:
        data = json.load(f)
        return data

def init_regex():
    '''
    init_regex(void) -> void
    
    inits patterns dictionary, which contains all regex patterns used in sorting tweets
    keys are: rt, media, hashtag, host, nominees, winner, presenter
    '''
    patterns = {
    
    "hashtag": [re.compile(r"#(\w+)", re.IGNORECASE)],
    "host": [re.compile(pattern, re.IGNORECASE) for pattern in [
    r"([A-Za-z\s]+)\s+(?:hosts?|hosting|kicks\s+off|hosted)\b",  # Matches various forms of hosting
    ]],
    "nominees": [re.compile(pattern, re.IGNORECASE) for pattern in [
    r"([A-Za-z\s]+)\s+(?:loses|was\s+nominated\s+for|deserved|didn't\s+get|should\s+have\s+won)\s+(best\s+\w+(?:\s\w+)*)",  # Matches various ways of discussing awards
    ]],
    "winner": [re.compile(r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+\w+(?:\s\w+)*)")],
    
    "presenter": [re.compile(pattern, re.IGNORECASE) for pattern in [
	r"([A-Za-z\s&]+?)\s+(?:is\s+presenting|to\s+present|presented|gives?\s+out|gave|is\s+announcing|announced|reveal(?:s|ed)?|hands?\s+(?:over|out)|unveil(?:s|ed)?|introduces?\s+nominees\s+for|just\s+presented|hosts?|awarding|brings?\s+out|steps\s+up\s+to\s+present|announces?\s+winner\s+of|presenting)\s+(?:the\s+)?(Best\s.+?)\b"
	]],
    
    "categories": [re.compile(
    r"Best ([\w\s]+) (in a ([\w\s]+)|goes to|is awarded to [\w\s]+)", re.IGNORECASE  # Match for Best in a category, goes to, or awarded
    )]
    
    }
    
    return patterns

def clean(text):
    '''
    clean(text: str) -> str
    cleans given text
    '''
    fixed = " ".join(text.split()).lower()
    return fixed
    
def sort(text, patterns, k):
    '''
    takes in tweet text and list of patterns, checks if tweet matches ANY patterns
    in list if so, return all possible findall matches in an array for entire list of
    patterns
    '''
    matches = []
    for p in patterns: #list of patterns for a given key, i.e. all patterns which are used for host
        match = p.findall(text)
        if match != []:
            #if k == 'presenter':
             #   print(match, p)
            matches.append(match)
    return matches
        
                


def init_and_sort(start):
    """__summary__: Parses through all tweets in datasets and checks them against all patterns
    for a given pattern key, for example, those that help find presenters, all successfully
    found matches are stored into a dataframe column corresponding to the key, then written to
    a file in df/<column name>
    """
    print("Enter dataset path: ")
    path ='gg2013.json'
    #path = input("> ")
    data = extract_data(path)
    patterns = init_regex()

    keys = patterns.keys()
    print(keys)
    r = r"^[\s\[']+|[\]']+$ "
    # pattern is only used when regex interprets [' ... '] as part
    # of the string
    cut = re.compile(r)
    
    sorted = {k: [] for k in keys}
    counts = {k: 0 for k in keys}
        #array with one column per key
        #in sorted, named the same, and initialized to fit all tweets in the dataset if necessary as
        #unsigned char(500)
        #counters to keep track of where we are in each column

    length = len(data)
    ttext = []
    #this array is similar to sorted and stores the actual tweet text that is extracted
    tmstmp = []
    #storage of timestamps, correlated with related tweet by index
    i=0
    early = float('inf')
    for tweet in data: #loop through each individual tweet
        cleaned = clean(tweet['text']) #first clean tweet for consistency and put into ttext
        ttext.append(cleaned)
        timestamp_ms = tweet['timestamp_ms']
        tmstmp.append(timestamp_ms)
        timestamp_ms = datetime.fromtimestamp(int(timestamp_ms/1000)) #find the earliest timestamp to use
        #in filtering tweets for host
        if i == 0:
            early = timestamp_ms
        elif timestamp_ms < early:
            early = timestamp_ms
        i += 1
    time_window = early + timedelta(minutes=30)

    for i in range(length):
        #all tweets are now populated, now loop through all tweets for pattern matching
        text = ttext[i]
        ms = tmstmp[i]
        ms = datetime.fromtimestamp(int(ms)/1000)
        #can make new json object here with only relevant info
        for k in keys: #for each pattern category like nominees, hosts, presenters
            df=sorted[k]
            rgx = patterns[k] #grab a pattern from list, check for matches and return all if there are any
            searched = sort(text, rgx, k)
            if (searched == []):
                continue
            curr = searched[0] #################
            if k == 'categories':
                if isinstance(curr[0], tuple):
                    cleaned =' in a '.join(curr[0])
                else:
                    cleaned=curr[0]
                df.append(cleaned)
                sorted[k]=df
                continue
            if k == 'presenter':
                df.append(curr[0])
                sorted[k] = df
                continue
            for j in range(len(curr)): #otherwise we want to split the tuples
                    slce = curr[j] #one tuple/list entry
                    if type(slce) == tuple: #if its nested take a guess
                        slce = slce[-1]
                    slce = re.sub(cut, '', slce) #refer to above
                
                    if k == 'host': #host function wants to check for certain time window, done below
                        if ms <= time_window:
                            df.append(slce)
                            sorted[k] = df
                        continue
                    df.append(slce)
                    sorted[k]=df
        i += 1
        if i % 20000 == 0:
            print("\n", time.time() - start, "seconds")
            print("sorted", i, "out of", length)
    res = sorted
    dfnom = res['nominees']
    dfshow = res['hashtag']
    dfhost = res['host']
    dfpresent = res['presenter']
    dfwin = res['winner']
    dfcat = res['categories']
    
    return dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat

def categories(df): #[('supporting actress', 'in a tv movie', 'tv movie')]
    data = []
    i=0
    while i < len(df):
        match = df[i]
        i += 1
        cleaned_match = re.sub(r'\s+(goes to|is|for).*', '', match)
            # Ensure the category starts with "Best"
        if not cleaned_match.startswith("best"):
            cleaned_match = "best " + cleaned_match
        data.append(cleaned_match)
    counts = Counter(data)
    counts_dict = {str(key): value for key, value in counts.items()}
    threshold = 5
    filtered_category_counts = {key: value for key, value in counts_dict.items() if value >= threshold}

    # Sort the filtered categories by their counts
    sorted_filtered_category_counts = sorted(filtered_category_counts.items(), key=lambda item: item[1], reverse=True)
    merged_category_counts = merge_similar_categories(sorted_filtered_category_counts)
    res = sorted(merged_category_counts.items(), key=lambda item: item[1], reverse=True)
    return res
    
def merge_similar_categories(categories, threshold=90):
    merged = {}
    for category, count in categories:
        found = False
        for existing_category in merged:
            if fuzz.ratio(category.lower(), existing_category.lower()) > threshold:
                merged[existing_category] += count
                found = True
                break
        if not found:
            merged[category] = count
    return merged


def nominees(df): #find possible nominees
    model = spacy.load('en_core_web_sm')
    i=0
    res=[]
    while i < len(df): # go through nominees col of df
        curr = df[i] 
        i += 1
        if type(curr) != str: #needs to be a string or invalid
            continue
        if curr == []:
            continue
        output = model(curr) #thin out results with entity matching and noun chunks
        for ent in output.ents:
            if ent.label_ == 'PERSON':
                res.append(ent.text)
        for chunk in output.noun_chunks:
            res.append(chunk.text)
            
    res_count = Counter(res) #count results
    return res_count    
    
    
def awardshow(df): #finding award show
    """Given all hashtag matches, returns most likely name for the award show

    Args:
        df (dataframe): pandas dataframe created with init_and_sort. For this function, relevant
        column is 'hashtag' which stores STRINGS, df['hashtag'][i] = <string>
        
    Returns:
        _type_: awardshow name string
    """
    counts = Counter(df) #count occurrences of each entry
    if counts:
        most_common_hashtag, count = counts.most_common(1)[0]
        print(f"The most mentioned hashtag is: #{most_common_hashtag}")
        print(f"Number of mentions: {count}")

        # Split the hashtag into words
        words = wordninja.split(most_common_hashtag)
        # Capitalize each word
        award_name = ' '.join(word.capitalize() for word in words)
        print(f"The award show name is: {award_name}")
        return award_name
    return

def hosts(df, show):
    """hosts(df, show) takes a dataframe containing relevant tweets and the awardshow name, and returns the top 2
    most likely hosts

    Args:
        df (dataframe): Pandas dataframe created with init_and_sort(). Relevant column is 'host'
        Entries can be tuples or strings depending on if dataframe was read or created
        show (string): award show name 
    """
    model = spacy.load('en_core_web_sm')
    potential_hosts = []
    normalized_award_name = clean(show.replace(' ', ''))
    i = 0
    while i < len(df): # Loop through all remaining rows
        curr = df[i] 
        i += 1
        if isinstance(curr, tuple): # If tuple transform into string
            curr = ' '.join(curr)
        split = re.split(r'\band\b|&', curr) # Split into individual hosts by any existing and/& in string
        for host in split:
            host = host.strip()
            if host:
                if normalized_award_name not in host.replace(' ', ' '):
                    potential_hosts.append(host)
        doc = model(curr)
        for ent in doc.ents: #Thinning results by checking entity label
            if ent.label_ == 'PERSON':
                host_name = clean(ent.text) #cleaning up
                host_name = ' '.join(host_name.split())
                if host_name:
                        # Exclude if host name contains award show name
                    if normalized_award_name not in host_name.replace(' ', ''):
                        potential_hosts.append(host_name)
    
    host_name_counts = Counter(potential_hosts)
    # Identify the top 2 most common host names
    if host_name_counts:
        most_common_hosts = host_name_counts.most_common(2)
        print("\nTop 2 most likely host(s):")
        for host, count in most_common_hosts:
            # Capitalize each word in the host name
            host_name_formatted = ' '.join(word.capitalize() for word in host.split())
            print(f"- {host_name_formatted}: mentioned {count} times")
    else:
        print("\nNo host names found.")       


def present(df_presenters):
    """
    Extracts presenter names and their corresponding awards from the 'presenter' column.

    Args:
        df_presenters (pd.Series): Series containing tuples of (presenter_text, award_text).

    Returns:
        list[tuple]: List of tuples (presenter_name, award_name).
    """
    # Load SpaCy model with only NER for efficiency
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger', 'lemmatizer'])

    options = []
    pattern_and = re.compile(r'\band\b|&', re.IGNORECASE)  # Pattern to split multiple presenters

    for item in df_presenters:
        # Ensure the item is a tuple with exactly two elements
        if not isinstance(item, tuple) or len(item) != 2:
            print(f"Skipping invalid entry")
            continue

        presenter_text, award_text = item

        # Skip if either part is empty or None
        if not presenter_text or not award_text:
            print(f"Skipping empty presenter or award {item}")
            continue

        # Clean and ensure the award starts with "Best"
        award_text = award_text.strip()
        if not award_text.lower().startswith('best'):
            award_text = 'Best ' + award_text.capitalize()

        # Preprocess presenter_text with wordninja
        # Remove any unwanted characters except '&' and 'and'
        presenter_text_clean = re.sub(r'[^\w\s&]', '', presenter_text)
        # Split concatenated words using wordninja
        split_presenter = wordninja.split(presenter_text_clean)
        # Capitalize properly
        split_presenter_cap = ' '.join([word.capitalize() for word in split_presenter])

        # Use SpaCy to extract PERSON entities from the cleaned presenter_text
        doc = nlp(split_presenter_cap)
        person_entities = [ent.text.strip() for ent in doc.ents if ent.label_ == 'PERSON']

        if not person_entities:
            #print(f"No PERSON entities found in presenter text at index {index}: '{presenter_text}'")
            continue

        for presenter in person_entities:
            # Split presenters connected by "and" or "&"
            individual_presenters = pattern_and.split(presenter)
            for person in individual_presenters:
                person = person.strip()
                if person:
                    # Append the (presenter, award) tuple
                    options.append( (person, award_text) )

    # Remove duplicates by converting the list of tuples to a set, then back to a list
    unique_pairs = list(set(options))

    print("\nList of presenter-award pairs:")
    for presenter, award in unique_pairs:
        print(f"Presenter: {presenter} - Award: {award}")

    return unique_pairs
 


def main():
    start = time.time()
       
        
    
    dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat = init_and_sort(start)
    cat = categories(dfcat)
    #print(cat)
    nom = nominees(dfnom)
    #print(nom)
    show = awardshow(dfshow)
    host = hosts(dfhost, show)
    presenters = present(dfpresent)
    
    print("\nRuntime of:", time.time() - start, "seconds")
    
    
if __name__ == "__main__":
    main()