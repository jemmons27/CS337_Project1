import numpy as np
import json
from langdetect import detect, detect_langs
import re
import pandas as pd
import time
from datetime import datetime, timedelta
import spacy
import wordninja
import difflib
from collections import Counter, defaultdict
from os import mkdir
from fuzzywuzzy import fuzz, process
import wordninja
from concurrent.futures import ThreadPoolExecutor, as_completed
from textblob import TextBlob
import csv


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
    r"([A-Za-z\s]+)\s+(?:hosts?|hosting|kicks\s+off|hosted)\b",  # Matches various forms of hosting
    r"hosts?\s+([A-Za-z\s]+)",  # Matches when someone is mentioned as a host
    r"hosted by\s+([A-Za-z\s]+)\b"  # Matches hosted by someone
    ]],
    "nominees": [re.compile(pattern, re.IGNORECASE) for pattern in [
    r"([A-Za-z\s]+)\s+(?:loses|is\s+nominated\s+for|was\s+nominated\s+for|deserved|didn't\s+get|should\s+have\s+won)\s+(best\s+\w+(?:\s\w+)*)",
    r"([A-Za-z\s]+)\s+(?:was\s+robbed|got\s+robbed)",
    r"([A-Za-z\s]+)\s+lost",
    r"the\s+nominees\s+for\s+([A-Za-z\s]+)\s+are\s+([A-Za-z\s,]+)\s+and\s+([A-Za-z\s]+)",
    r"\b(?:see|hope|wish)(?:\s+\w+)*\s+(\w+(?: \w+)*)\s+win[s]?\b"
]],
    "winner": [re.compile(r"([A-Za-z\s]+)\s+(wins|won by|receives|received|takes|sweeps)\s+.*?\b(best\s+\w+(?:\s\w+)*)")],
    
    "presenter": [re.compile(pattern, re.IGNORECASE) for pattern in [
    r"([A-Za-z\s&]+?)\s+(?:is\s+presenting|to\s+present|presented|gives?\s+out|gave|is\s+announcing|announced|reveal(?:s|ed)?|hands?\s+(?:over|out)|unveil(?:s|ed)?|introduces?\s+nominees\s+for|just\s+presented|hosts?|awarding|brings?\s+out|steps\s+up\s+to\s+present|announces?\s+winner\s+of|presenting)\s+(?:the\s+)?(Best\s.+?)\b"
    ]],
    
    "categories": [re.compile(
    r"Best ([\w\s]+) (in a (?:[\w\s]+)|goes to|is awarded to [\w\s]+)", re.IGNORECASE  # Match for Best in a category, goes to, or awarded
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

def init_and_sort(write, start):
    """Parses through all tweets in datasets and checks them against patterns for a given key.
    Matches are stored in a dataframe column and written to a file in df/<column name>.
    """
    print("Enter dataset path: ")
    path = 'gg2013.json'
    # path = input("> ")
    data = extract_data(path)
    patterns = init_regex()

    keys = patterns.keys()
    print(keys)
    r = r"^[\s\[']+|[\]']+$ "
    cut = re.compile(r)

    sorted_data = {k: np.empty(len(data), dtype=object if k == 'presenter' else np.dtype('U500')) for k in keys}
    counts = {k: 0 for k in keys}
    df = pd.DataFrame.from_dict(sorted_data)

    length = len(data)
    ttext = np.empty(length, dtype=np.dtype('U500'))
    tmstmp = np.empty(length, dtype=int)

    early = datetime.max
    for i, tweet in enumerate(data):
        cleaned = clean(tweet['text'])
        ttext[i] = cleaned
        timestamp_ms = tweet['timestamp_ms']
        tmstmp[i] = timestamp_ms
        timestamp_dt = datetime.fromtimestamp(int(timestamp_ms) / 1000)
        if timestamp_dt < early:
            early = timestamp_dt

    time_window = early + timedelta(minutes=30)

    def process_tweet(i):
        text = ttext[i]
        ms = tmstmp[i]
        ms_dt = datetime.fromtimestamp(int(ms) / 1000)
        results = []
        seen = {k: set() for k in keys}  # Initialize seen sets for each pattern key

        for k in keys:
            rgx = patterns[k]
            searched = sort(text, rgx, k)
            if not searched:
                continue
            curr = searched[0]
            ind = counts[k]
            if k == 'winner':
                if len(curr[0]) >= 5 and curr[0] not in seen[k]:
                    results.append((k, ind, curr[0]))
                    seen[k].add(curr[0])
                    counts[k] = ind + 1
                continue
            if k == 'presenter':
                if len(curr[0]) >= 5 and curr[0] not in seen[k]:
                    results.append((k, ind, curr[0]))
                    seen[k].add(curr[0])
                    counts[k] = ind + 1
                continue
            if k == 'categories':
                cleaned = ' '.join(curr[0]) if isinstance(curr[0], tuple) else curr[0]
                if len(cleaned) >= 5 and cleaned not in seen[k]:
                    results.append((k, ind, cleaned))
                    seen[k].add(cleaned)
                    counts[k] = ind + 1
                continue
            for j in range(len(curr)):
                slce = curr[j]
                if isinstance(slce, tuple):
                    slce = slce[-1]
                slce = re.sub(cut, '', slce)
                if len(slce) < 5 or slce in seen[k]:
                    continue
                if k == 'host' and ms_dt <= time_window:
                    results.append((k, ind, slce))
                    seen[k].add(slce)
                    counts[k] = ind + 1
                    continue
                results.append((k, ind, slce))
                seen[k].add(slce)
                counts[k] = ind + 1
        return results

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_tweet, i) for i in range(length)]
        for future in as_completed(futures):
            results = future.result()
            for k, ind, value in results:
                df.at[ind, k] = value

    tweetdf = pd.DataFrame.from_dict({'ttext': ttext, 'tmstmp': tmstmp})
    tweetdf.to_csv('tweetdf3.csv', sep='\t', index=False)

    res = {}
    for k in keys:
        mask = df[k].replace('', np.nan).dropna()
        if write:
            mask.to_csv(f'df/{k}.csv', sep='\t', index=False)
        res[k] = mask

    dfnom = res['nominees']
    dfshow = res['hashtag']
    dfhost = res['host']
    dfpresent = res['presenter']
    dfwin = res['winner']
    dfcat = res['categories']

    return dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat


def categories(df): #[('supporting actress', 'in a tv movie', 'tv movie')]
    data = []
    i = 0
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
    """__summary__: Parses through all tweets in datasets and checks them against all patterns
    for a given pattern key, for example, those that help find presenters, all successfully
    found matches are stored into a dataframe column corresponding to the key, then written to
    a file in df/<column name>
    """
    print("Enter dataset path: ")
    path = 'gg2013.json'
    # path = input("> ")
    data = extract_data(path)
    patterns = init_regex()

    keys = patterns.keys()
    print(keys)
    r = r"^[\s\[']+|[\]']+$ "
    cut = re.compile(r)

    sorted_data = {k: np.empty(len(data), dtype=object if k == 'presenter' else np.dtype('U500')) for k in keys}
    counts = {k: 0 for k in keys}
    df = pd.DataFrame.from_dict(sorted_data)

    length = len(data)
    ttext = np.empty(length, dtype=np.dtype('U500'))
    tmstmp = np.empty(length, dtype=int)

    early = datetime.max
    for i, tweet in enumerate(data):
        cleaned = clean(tweet['text'])
        ttext[i] = cleaned
        timestamp_ms = tweet['timestamp_ms']
        tmstmp[i] = timestamp_ms
        timestamp_dt = datetime.fromtimestamp(int(timestamp_ms) / 1000)
        if timestamp_dt < early:
            early = timestamp_ms

    time_window = early + timedelta(minutes=30)

    def process_tweet(i):
        text = ttext[i]
        ms = tmstmp[i]
        ms= datetime.fromtimestamp(int(ms) / 1000)
        results = []

        for k in keys:
            rgx = patterns[k]
            searched = sort(text, rgx, k)
            if not searched:
                continue
            curr = searched[0]
            ind = counts[k]
            if k == 'winner':
                results.append((k, ind, curr[0]))
                counts[k] = ind + 1
                continue
            if k == 'presenter':
                results.append((k, ind, curr[0]))
                counts[k] = ind + 1
                continue
            if k == 'categories':
                cleaned = ' '.join(curr[0]) if isinstance(curr[0], tuple) else curr[0]
                results.append((k, ind, cleaned))
                counts[k] = ind + 1
                continue
            for j in range(len(curr)):
                slce = curr[j]
                if isinstance(slce, tuple):
                    slce = slce[-1]
                slce = re.sub(cut, '', slce)
                if k == 'host' and ms <= time_window:
                    results.append((k, ind, slce))
                    counts[k] = ind + 1
                    continue
                results.append((k, ind, slce))
                counts[k] = ind + 1
        return results

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_tweet, i) for i in range(length)]
        for future in as_completed(futures):
            results = future.result()
            for k, ind, value in results:
                df.at[ind, k] = value

    tweetdf = pd.DataFrame.from_dict({'ttext': ttext, 'tmstmp': tmstmp})
    tweetdf.to_csv('tweetdf3.csv', sep='\t', index=False)

    res = {}
    for k in keys:
        mask = df[k].replace('', np.nan).dropna()
        if write:
            mask.to_csv(f'df/{k}.csv', sep='\t', index=False)
        res[k] = mask

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

def load_nominees(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        nominees = [row[0].strip() for row in reader if row]
    return nominees




#maps nominees to categories
def map_nominees_to_categories(correct_categories):
    nominees = load_nominees('./df/nominees.csv')
    with open('./gg2013.json', 'r') as file:
        tweets = json.load(file)

    nominee_to_categories = defaultdict(list)
    category_patterns = {category: re.compile(re.escape(category), re.IGNORECASE) for category in correct_categories}
    nominee_patterns = {nominee: re.compile(re.escape(nominee), re.IGNORECASE) for nominee in nominees}

    for tweet in tweets:
        text = tweet.get("text", "")

        for nominee, nominee_pattern in nominee_patterns.items():
            if len(nominee) > 4 and nominee_pattern.search(text):
                for category, category_pattern in category_patterns.items():
                    if category_pattern.search(text):
                        if nominee not in nominee_to_categories[category] and "nominee" not in nominee:
                            nominee_to_categories[category].append(nominee)
    
    return dict(nominee_to_categories)
    
    
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
    res=[]
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
            res.append(host_name_formatted)
    return res     


def present(df_presenters, categories):
    """
    Extracts presenter names and maps their awards to the closest official categories.

    Args:
        df_presenters (pd.Series): Series containing tuples of (presenter_text, award_text).
        official_categories (list): List of official award categories.

    Returns:
        list[tuple]: List of tuples (presenter_name, matched_official_category).
    """
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger'])
    options = []
    pattern_and = re.compile(r'\band\b|&', re.IGNORECASE)

    for _, item in df_presenters.items():
        if not isinstance(item, tuple) or len(item) != 2:
            continue
        presenter_text, award_text = item
        if not presenter_text or not award_text:
            continue
        award_text = award_text.strip()
        if not award_text.lower().startswith('best'):
            award_text = 'Best ' + award_text.capitalize()
        presenter_text_clean = re.sub(r'[^\w\s&]', '', presenter_text)
        split_presenter = wordninja.split(presenter_text_clean)
        split_presenter_cap = ' '.join(word.capitalize() for word in split_presenter)
        doc = nlp(split_presenter_cap)
        person_entities = [ent.text.strip() for ent in doc.ents if ent.label_ == 'PERSON']
        if not person_entities:
            continue
        for presenter in person_entities:
            individual_presenters = pattern_and.split(presenter)
            for person in individual_presenters:
                person = person.strip()
                if person:
                    options.append((person, award_text))
    
    unique_pairs = list(set(options))
    mapped_pairs = []
    for presenter, award in unique_pairs:
        match = process.extractOne(award, categories, scorer=fuzz.WRatio)
        if match:
            closest_category = match[0]
            mapped_pairs.append((presenter, closest_category))
        else:
            mapped_pairs.append((presenter, award))
    
    return mapped_pairs



def find_winners(df, categories):
    
    answers = {}
    i = 0

    while i < len(df):
        # split = df[i].split(",")
        person = df[i][0]
        query = df[i][2]
        maxAward = []
        maxSeq = 0
        for award in categories:
            seq = difflib.SequenceMatcher(a=query.lower(), b=award.lower())
            if seq.ratio() >= maxSeq:
                maxAward.append(award)
                maxSeq = seq.ratio()
        if len(maxAward) > 1:
            query_words = set(query.lower().split())
            maxAward = max(maxAward, key=lambda award: len(query_words.intersection(award.lower().split())))
            if answers.get(maxAward) == None:
                answers[maxAward] = []
                answers[maxAward].append(person)
        i += 1
    top_mentions = {}
    for award, people in answers.items():
        person_counts = Counter(people)
        # Get the top 3 most common people
        top_mentions[award] = [person for person, count in person_counts.most_common(3)]
    
    return top_mentions

import json
import spacy
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict

def analyze_parties(tweets_file_path):
    """
    Analyzes party mentions and sentiments from tweets loaded from a JSON file.
    
    Args:
        tweets_file_path (str): Path to the JSON file containing tweets.
    
    Returns:
        dict: {
            'party_mentions': dict,
            'party_avg_sentiment': dict,
            'most_attended_party': str or None,
            'party_with_highest_sentiment': str or None
        }
    """
    nlp = spacy.load('en_core_web_sm')
    party_keywords = ['party', 'after-party', 'afterparty', 'celebration', 'gala']
    party_counter = Counter()
    party_sentiment = defaultdict(list)
    
    def analyze_sentiment(text):
        return TextBlob(text).sentiment.polarity
    
    def extract_parties(text):
        doc = nlp(text)
        return [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'EVENT'] and any(keyword in ent.text.lower() for keyword in party_keywords)]
    
    # Load tweets from the JSON file
    try:
        with open(tweets_file_path, 'r', encoding='utf-8') as file:
            tweets = json.load(file)
    except FileNotFoundError:
        print(f"Tweets file not found at path: {tweets_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the tweets file at path: {tweets_file_path}")
        return {}
    
    def process_tweets(tweets):
        texts = [tweet['text'] for tweet in tweets]
        docs = list(nlp.pipe(texts, batch_size=50))
        for tweet, doc in zip(tweets, docs):
            parties = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'EVENT'] and any(keyword in ent.text.lower() for keyword in party_keywords)]
            if parties:
                tweet['parties'] = parties
                tweet['sentiment'] = analyze_sentiment(tweet['text'])
        return tweets
    
    # Process the tweets in parallel
    batch_size = 100
    processed_data = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_tweets, tweets[i:i + batch_size]) for i in range(0, len(tweets), batch_size)]
        for future in as_completed(futures):
            processed_data.extend(future.result())
    
    # Count party mentions and aggregate sentiment
    for tweet in processed_data:
        if 'parties' in tweet:
            for party in tweet['parties']:
                party_counter[party] += 1
                party_sentiment[party].append(tweet['sentiment'])
    
    # Calculate average sentiment for each party
    party_avg_sentiment = {party: sum(sentiments) / len(sentiments) for party, sentiments in party_sentiment.items()}
    
    most_attended_party = max(party_counter, key=party_counter.get) if party_counter else None
    party_with_highest_sentiment = max(party_avg_sentiment, key=party_avg_sentiment.get) if party_avg_sentiment else None
    
    return {
        'party_mentions': dict(party_counter),
        'party_avg_sentiment': party_avg_sentiment,
        'most_attended_party': most_attended_party,
        'party_with_highest_sentiment': party_with_highest_sentiment
    }


def construct_output(show, hosts, presenters, winners, nominees, official_categories):
    """
    Constructs the final JSON output with hosts and award data.
    
    Args:
        show (str): Name of the award show.
        hosts (list): List of host names.
        presenters (list[tuple]): List of tuples (presenter_name, matched_official_category).
        winners (dict): Dictionary mapping categories to winners.
        nominees (dict): Dictionary mapping categories to nominees.
        official_categories (list): List of official award categories.
    
    Returns:
        dict: Structured JSON output.
    """
    award_data = {category: {"nominees": nominees.get(category, []),
                             "presenters": [],
                             "winner": winners.get(category, "")}
                  for category in official_categories}
    
    for presenter, category in presenters:
        if category in award_data:
            award_data[category]["presenters"].append(presenter)
    
    output = {
        "Award show": show,
        "hosts": hosts,
        "award_data": award_data
    }
    
    return output

#Format in human-readable form

def format_human_readable(output, party_analysis):
    """
    Formats the award show data into a human-readable string, including party analysis.
    
    Args:
        output (dict): The structured JSON output.
        party_analysis (dict): Party analysis results.
    
    Returns:
        str: Human-readable formatted string.
    """
    lines = []
    lines.append(f"Award show: {output.get('Award show', '')}\n")
    
    hosts = output.get('hosts', [])
    if hosts:
        lines.append(f"Hosts: {', '.join(hosts)}\n")
    
    for category, details in output.get('award_data', {}).items():
        lines.append(f"Award: {category}")
        if details["presenters"]:
            lines.append(f"Presenters: {', '.join(details['presenters'])}")
        if details["nominees"]:
            nominees_str = ', '.join(f'"{nom}"' for nom in details["nominees"])
            lines.append(f"Nominees: {nominees_str}")
        if details["winner"]:
            lines.append(f"Winner: \"{details['winner']}\"\n")
        else:
            lines.append("")  # Add a newline if there's no winner
    
    # Add Party Analysis
    if party_analysis:
        most_attended_party = party_analysis.get('most_attended_party')
        party_with_highest_sentiment = party_analysis.get('party_with_highest_sentiment')
        party_avg_sentiment = party_analysis.get('party_avg_sentiment', {})
        
        if most_attended_party:
            mentions = party_analysis.get('party_mentions', {}).get(most_attended_party, 0)
            lines.append(f"Most attended party: {most_attended_party} ({mentions} mentions)")
        
        if party_with_highest_sentiment:
            sentiment_score = party_avg_sentiment.get(party_with_highest_sentiment, 0)
            sentiment = "positive" if sentiment_score > 0 else "negative"
            lines.append(f"Party with highest sentiment: {party_with_highest_sentiment} ({sentiment}, score: {sentiment_score:.2f})")
    
    return '\n'.join(lines)

def main():
    start = time.time()
    simplefilter(action="ignore", category=FutureWarning)
    x = input("Read from precreated files? [y/n] > ")
    if x == 'y':
        dfnom = pd.read_csv('df/nominees.csv', sep='\t', encoding='utf-8')
        dfnom = dfnom['nominees']
        dfshow = pd.read_csv('df/hashtag.csv', sep='\t', encoding='utf-8')
        dfshow = dfshow['hashtag']
        dfhost = pd.read_csv('df/host.csv', sep='\t', encoding='utf-8')
        dfhost = dfhost['host']
        dfpresent = pd.read_csv('df/presenter.csv', sep='\t', encoding = 'utf-8')
        dfpresent = dfpresent['presenter']
        dfcat = pd.read_csv('df/categories.csv', sep='\t', encoding = 'utf-8')
        dfcat = dfcat['categories']
        dfwin = pd.read_csv('df/winner.csv', sep='\t', encoding = 'utf-8')
        dfwin = dfwin['winner']
    else:
        write = input("Write sorted results to csv files? [y/n] > ")
        if write == 'y':
            write = True
        else:
            write = False
        directory = 'df'
        
        try:
            mkdir(directory)
            print(f"Directory '{directory}' created successfully.")
        except FileExistsError:
            print(f"Directory '{directory}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{directory}'.")
        except Exception as e:
            print(f"An error occurred: {e}")
        dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat = init_and_sort(write, start)
    # cat = categories(dfcat)
    # final_categories = merge_similar_categories(cat)
    #print(cat)
    # nom = nominees(dfnom)
    # print(nom)
    # show = awardshow(dfshow)
    # host = hosts(dfhost, show)
    # presenters = present(dfpresent,final_categories)
    # winners = find_winners(dfwin, final_categories)
    # print(winners)
    
    # print("PARTIES")
    # parties= analyze_parties('gg2013.json')
    # print(parties)
    

    correct_categories = [
    'best screenplay - motion picture', 'best director - motion picture', 
    'best performance by an actress in a television series - comedy or musical', 
    'best foreign language film', 'best performance by an actor in a supporting role in a motion picture', 
    'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 
    'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 
    'best mini-series or motion picture made for television', 'best original score - motion picture', 
    'best performance by an actress in a television series - drama', 'best performance by an actress in a motion picture - drama', 
    'cecil b. demille award', 'best performance by an actor in a motion picture - comedy or musical', 
    'best motion picture - drama', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television', 
    'best performance by an actress in a supporting role in a motion picture', 'best television series - drama', 
    'best performance by an actor in a mini-series or motion picture made for television', 
    'best performance by an actress in a mini-series or motion picture made for television', 
    'best animated feature film', 'best original song - motion picture', 
    'best performance by an actor in a motion picture - drama', 'best television series - comedy or musical', 
    'best performance by an actor in a television series - drama', 'best performance by an actor in a television series - comedy or musical'
]
    # Map nominees to categories
    nominee_to_categories = map_nominees_to_categories(correct_categories)
    # Print each item with a newline in between
    for category, nominees in nominee_to_categories.items():
        print(f"{category}: {nominees}\n")

    print("\nRuntime of:", time.time() - start, "seconds")

    
    
if __name__ == "__main__":
    main()

    