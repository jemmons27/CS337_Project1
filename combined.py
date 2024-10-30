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
import ast

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
    
    "rt": [re.compile(r'RT\s@')],
    "media": [re.compile(r'https?:\/\/t\.co\/', re.IGNORECASE)],
    "hashtag": [re.compile(r"#(\w+)", re.IGNORECASE)],
    "host": [re.compile(pattern, re.IGNORECASE) for pattern in [
        r"([A-Za-z\s]+)\s+hosts?\b",
        r"([A-Za-z\s]+)\.\.\.\s*hosting\b",
        r"([A-Za-z\s]+)\s+kicks\s+off\b",
        r"Hosts?\s+([A-Za-z\s]+)",
        r"([A-Za-z\s]+)\s+hosted\b",
        r"hosted by\s+([A-Za-z\s]+)\b"
    ]],
    "nominees": [re.compile(pattern, re.IGNORECASE) for pattern in [r"([A-Za-z\s]+)\s+loses\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+was\s+nominated\s+for\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+deserved\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+didn't\s+get\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+should\s+have\s+won\s+(best\s+\w+(?:\s\w+)*)",
          r"([A-Za-z\s]+)\s+was\s+robbed",
          r"([A-Za-z\s]+)\s+got\s+robbed",
          r"([A-Za-z\s]+)\s+lost"]],
    "winner": [re.compile(r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+\w+(?:\s\w+)*)")],
    
    "presenter": [re.compile(pattern, re.IGNORECASE) for pattern in [
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
    r"([A-Za-z\s&]+?)\s+gives?\s+(?:the\s+)?(.+?)\s+to\s+([A-Za-z\s&]+?)\b"]]
    }
    
    return patterns

def clean(text):
    '''
    clean(text: str) -> str
    cleans given text
    '''
    fixed = " ".join(text.split()).lower()
    return fixed
    
def sort(text, patterns):
    '''
    takes in tweet text and list of patterns, checks if tweet matches ANY patterns
    in list if so, return all possible findall matches in an array for entire list of
    patterns
    '''
    matches = []
    for p in patterns: #list of patterns for a given key, i.e. all patterns which are used for host
        match = p.search(text)
        if match != None:
            matches.append(p.findall(text))
    return matches
        
                


def init_and_sort():
    """__summary__: Parses through all tweets in datasets and checks them against all patterns
    for a given pattern key, for example, those that help find presenters, all successfully
    found matches are stored into a dataframe column corresponding to the key

    Returns:
        dataframe: One column per set of patterns, contains all found matches either in tuples or strings,
        depending on the needs of the related functions
    """
    print("Enter dataset path: ")
    path ='gg2013.json'
    #path = input("> ")
    data = extract_data(path)
    patterns = init_regex()

    keys = patterns.keys()
    
    r = r"^[\s\[']+|[\]']+$ "
    # pattern is only used when regex interprets [' ... '] as part
    # of the string
    cut = re.compile(r)
    
    sorted = {}
    counts = {}
    for k in keys:
        sorted.update({k: np.empty(len(data), np.dtype('U500'))}) # numpy array with one column per key
        #in sorted, named the same, and initialized to fit all tweets in the dataset if necessary as
        #unsigned char(500)
        counts.update({k: 0})
        #counters to keep track of where we are in each column
    df = pd.DataFrame.from_dict(sorted)

    length = len(data)
    ttext = np.empty(length, dtype = np.dtype('U500'))
    #this array is similar to sorted and stores the actual tweet text that is extracted
    tmstmp = np.empty(length, dtype=int)
    #storage of timestamps, correlated with related tweet by index
    i=0
    early = float('inf')
    for tweet in data: #loop through each individual tweet
        cleaned = clean(tweet['text']) #first clean tweet for consistency and put into ttext
        ttext[i] = cleaned
        timestamp_ms = tweet['timestamp_ms']
        tmstmp[i] = timestamp_ms
        timestamp_ms = datetime.fromtimestamp(int(timestamp_ms/1000)) #find the earliest timestamp to use
        #in filtering tweets for host
        if i == 0:
            early = timestamp_ms
        elif timestamp_ms < early:
            early = timestamp_ms
        i += 1
    tweetdf = pd.DataFrame.from_dict({'ttext': ttext, 'tmstmp': tmstmp})
    time_window = early + timedelta(minutes=30)
    print(time_window)
    
    for i in range(length):
        #all tweets are now populated, now loop through all tweets for pattern matching
        text = tweetdf['ttext'][i] 
        ms = tweetdf["tmstmp"][i]
        ms = datetime.fromtimestamp(int(ms)/1000)
        #can make new json object here with only relevant info
        for k in keys: #for each pattern category like nominees, hosts, presenters
            rgx = patterns[k] #grab a pattern from list, check for matches and return all if there are any
            searched = sort(text, rgx)
            if searched == []:
                continue
            curr = searched[0]
            ind = counts[k]
            if k == 'presenter': #presenter function prefers tuples/lists of strings, this part preserves tuples only for
                                 #presenter patterns
                df[k][ind] = curr[0]
                counts[k] = ind + 1
                continue
            for j in range(len(curr)): #otherwise we want to split the tuples
                slce = curr[j] #one tuple/list entry
                if type(slce) == tuple: #if its nested take a guess
                    slce = slce[-1]
                slce = re.sub(cut, '', slce) #refer to above
                if k == 'host': #host function wants to check for certain time window, done below
                    if ms <= time_window:
                        df[k][ind] = slce
                        counts[k] = ind + 1
                        continue
                df[k][ind] = slce
                counts[k] = ind + 1
        i += 1
        if i % 20000 == 0:
            print("pattern matching:", i, "out of:", length)
    print(df)
    tweetdf.to_csv('tweetdf2.csv', index=False) #save to csv for testing/quicker running
    df.to_csv('sorted2.csv', sep='\t', encoding='utf-8',index=False)
    return df #return the populated dataframe

def nominees(df): #find possible nominees
    model = spacy.load('en_core_web_sm')
    i=0
    res=[]
    while i < len(df['nominees']): # go through nominees col of df
        curr = df['nominees'][i] 
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
    mask = df['hashtag'].replace('', np.nan) #get rid of all extra rows
    mask.dropna( inplace=True)
    counts = Counter(mask) #count occurrences of each entry
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
    model = spacy.load('en_core_web_sm')
    potential_hosts = []
    normalized_award_name = clean(show.replace(' ', ''))
    i = 0
    while i < len(df['host']):
        curr = df['host'][i]
        i += 1
        if type(curr) != str:
            continue
        split = re.split(r'\band\b|&', curr)
        for host in split:
            host = host.strip()
            if host:
                if normalized_award_name not in host.replace(' ', ' '):
                    potential_hosts.append(host)
        doc = model(curr)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                host_name = clean(ent.text)
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


def present(df):
    mask = df['presenter']
    mask.dropna(inplace=True)
    #print(mask)
    i = 0
    model = spacy.load('en_core_web_sm')
    pat = r'\band\b|&'
    pat = re.compile(pat)
    options = []
    strhandler = re.compile(r"'([^']*)'")
    while i < len(mask):
        curr = mask[i]
        if type(curr) == str:
            matches = re.findall(strhandler, curr)
            curr = (matches[0:-1])
        i += 1
        if len(curr) == 2:
            entity_part, _ = curr
        elif len(curr) == 3:
            # Handle patterns with two entities (e.g., presenters connected by 'and')
            #print(pat.search(' '.join(curr.split())))
            entity_part = f"{curr[0]} and {curr[1]}"
            '''
            if pat.search(curr):
                entity_part = f"{curr[0]} and {curr[1]}"
            else:
                entity_part = curr[0]
                '''
        else:
            continue  # Skip if the match doesn't fit expected patterns 
        doc = model(entity_part)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                presenter_name = ent.text.strip()
                # Handle multiple presenters connected by 'and' or '&'
                individual_presenters = re.split(r'\band\b|&', presenter_name)
                for person in individual_presenters:
                    person = person.strip()
                    if person:
                        options.append(person)
    #print(options)
    # Remove duplicates by converting to a set, then back to a list
    unique_presenters = list(set(options))

    print("\nList of potential presenters:")
    for presenter in unique_presenters:
        print(presenter)

    return unique_presenters

def main():
    simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
    simplefilter(action="ignore", category=FutureWarning)
    simplefilter(action="ignore", category=pd.errors.SettingWithCopyWarning)
    #df = init_and_sort()
    df = pd.read_csv('sorted2.csv', sep='\t', encoding='utf-8')
    nom = nominees(df)
    print(nom)
    show = awardshow(df)
    host = hosts(df, show)
    presenters = present(df)
    
if __name__ == "__main__":
    start = time.time()
    main()
    print("\nRuntime of:", time.time() - start, "seconds")