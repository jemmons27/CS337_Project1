import numpy as np
import json
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
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv


###THIS FILE IS RUN FROM gg_api.py!!!!!! It needs year input and tmp, which is the result of
#some shenanigans with the hardcoded categories to make them work with the presenters function

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
	r"([A-Za-z\s]+)\s+(?:loses|was\s+nominated\s+for|deserved|didn't\s+get|should\s+have\s+won)\s+(best\s+\w+(?:\s\w+)*)",  # Matches various ways of discussing awards
	r"([A-Za-z\s]+)\s+(?:was\s+robbed|got\s+robbed)",  # Matches cases where an entity was robbed
	r"([A-Za-z\s]+)\s+lost"  # Matches simple loss
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
		
				


def init_and_sort(start, year):
	"""__summary__: Parses through all tweets in datasets and checks them against all patterns
	for a given pattern key, for example, those that help find presenters, all successfully
	found matches are stored into a dataframe column corresponding to the key, then written to
	a file in df/<column name>
	"""
	print("Enter dataset path: ")
	path ="gg" + year + ".json"
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
					cleaned =' '.join(curr[0])
				else:
					cleaned=curr[0]
				df.append(cleaned)
				sorted[k]=df
				continue
			if k == 'presenter':
				df.append(curr[0])
				sorted[k] = df
				continue
			if k == 'winner':
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


def nominees(tweets, award_categories, nominees):
	nominee_to_categories = defaultdict(list)
	category_patterns = {category: re.compile(re.escape(category), re.IGNORECASE) for category in award_categories.keys()}
	nominee_patterns = {nominee: re.compile(re.escape(nominee), re.IGNORECASE) for nominee in nominees}

	for tweet in tweets:
		text = tweet.get("text", "")
		for nominee, nominee_pattern in nominee_patterns.items():
			if nominee_pattern.search(text):
				for category, category_pattern in category_patterns.items():
					if category_pattern.search(text):
						if nominee not in nominee_to_categories[category]:
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
	res = []
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
			res.append(host_name_formatted)
	else:
		print("\nNo host names found.")   

	return res    


def present(df_presenters, cat):
	"""
	Extracts presenter names and maps their awards to the closest official categories.

	Args:
		df_presenters (pd.Series): Series containing tuples of (presenter_text, award_text).
		official_categories (list): List of official award categories.

	Returns:
		list[tuple]: List of tuples (presenter_name, matched_official_category).
	"""
	# Load SpaCy model with only NER for efficiency
	nlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger', 'lemmatizer'])

	options = []
	pattern_and = re.compile(r'\band\b|&', re.IGNORECASE)

	for item in df_presenters:
		# Ensure the item is a tuple with exactly two elements
		if not isinstance(item, tuple) or len(item) != 2:
			print(f"Skipping invalid entry")
			continue
		presenter_text, award_text = item
		if not presenter_text or not award_text:
			print(f"Skipping empty presenter or award {item}")
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
		match = process.extractOne(award, cat, scorer=fuzz.WRatio)
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


## MAPPING NOMINEES TO CATEGORIES
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

def load_nominees(file_path):
	with open(file_path, 'r') as file:
		reader = csv.reader(file)
		nominees = [row[0].strip() for row in reader if row]
	return nominees

def map_nominees_to_categories(tweets, correct_categories, nominees):
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

#####


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

 

def cat_match(cat, real, tshld):
	res = {i: [] for i in real}
	for tup in cat:
		entry = tup[0]
		print(entry)
		for i in real:
			if (fuzz.ratio(entry, i)) > tshld:
				tmp = res[i]
				tmp.append(entry)
				res[i] = tmp
	print(res)
	return res

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
		if isinstance(category, list):
			category = max(category, key=len)
		if category in award_data:
			award_data[category]["presenters"].append(presenter)
	
	output = {
		"Award show": show,
		"hosts": hosts,
		"award_data": award_data
	}
	
	return output

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
	return lines

def store_results(data_lists, year):
    for l in data_lists:
        path = l + year + ".json"
        with (open(path, 'w', encoding='utf-8')) as f:
            json.dump(data_lists[l], f)
            f.close()
    
    

def main(year, tmp):
    start = time.time()
    #dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat = init_and_sort(start, year)
    path = 'gg' + year + 'categories.json'
    with open(path, 'r') as f:
        correct_categories = json.load(f) 
    #real=award_categories_answers(fpath)
    #print(real)
    #matched_categories = cat_match(cat, real, tshld=70)
    path = "show" + year + ".json"
    with (open(path, 'r')) as f:
        dfshow = json.load(f)
    show = awardshow(dfshow)
    path = 'hosts' + year + '.json'
    with open(path, 'r') as f:
        dfhost = json.load(f)
    host = hosts(dfhost, show)
    path = 'presenters' + year + '.json'
    with open(path, 'r') as f:
        presenter_data = json.load(f)
    fixed = []
    for entry in presenter_data:
        fixed.append(tuple(entry))
    print('presenters')
    presenters = present(fixed, tmp)
    path = 'winners' + year + '.json'
    with (open(path, 'r')) as f:
        winner_data = json.load(f)
    winners_to_cat = find_winners(winner_data, correct_categories)
	
	## nominees to categories
    tweets_file_path = "gg2013.json"
    path = 'nominees' + year + '.json'
	# Load data
    with open(tweets_file_path, 'r') as file:
        tweets = json.load(file)
    nominees = load_nominees(path)
	# Map nominees to categories
    nominee_to_categories = map_nominees_to_categories(tweets, correct_categories, nominees)
    print("CATEGORIES TO NOMINEES: ")
    for category, nominees in nominee_to_categories.items():
        print(f"{category}: {nominees}\n")

    print("PARTIES")
    parties= analyze_parties('gg2013.json')
    print(parties)
	
    json_output = construct_output(show, host, presenters, winners_to_cat, nominee_to_categories, correct_categories)
    with open('gg' + year + 'json_output.json', 'w') as f:
        json.dump(json_output, f)
    print("OUTPUT:")
	# print(json_output)
    human_output = format_human_readable(json_output, parties)
    with open('gg' + year + 'human_output.txt', 'w') as f:
        json.dump(human_output, f)
    print(human_output)
	
    print("\nRuntime of:", time.time() - start, "seconds")
	

if __name__ == "__main__":
    main()