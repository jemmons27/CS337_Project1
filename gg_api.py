'''Version 0.4'''
import main as m
import time
import json

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    path = "show" + year + ".json"
    with (open(path, 'r')) as f:
        show_data = json.load(f)
    show = m.awardshow(show_data)
    path = 'hosts' + year + '.json'
    with open(path, 'r') as f:
        host_data = json.load(f)
    hosts = m.hosts(host_data, show)
    
    
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    path = "categories" + year + ".json"
    with (open(path, 'r')) as f:
        category_data = json.load(f)
    counts = m.categories(category_data)
    cats = m.merge_similar_categories(counts)
    awards=cats
    return awards

def get_nominees(year): ### NEEDS TO BE DONE
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    path = 'nominees' + year + '.json' ###Temp code so that it works with autograder
    with (open(path, 'r')) as f:
        nominee_data = json.load(f)
    for i in range(len(nominee_data)):
        nominee_data[i] = nominee_data[i].strip()
        
    path = 'gg' + year + 'categories.json'
    with (open(path, 'r')) as f:
        categories = json.load(f)
    nominees = {}
    path = 'gg' + year + '.json'
    with (open(path, 'r')) as f:
        tweet_data = json.load(f)
    tmp = {}
    for cat in categories:
        tmp[cat] = cat
    nominees = m.map_nominees_to_categories(tweet_data, tmp, nominee_data)
    for cat in categories:
        if cat not in nominees.keys():
            nominees[cat] = []
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    path = 'winners' + year + '.json'
    with (open(path, 'r')) as f:
        winner_data = json.load(f)
    path = 'gg' + year + 'categories.json'
    with (open(path, 'r')) as f:
        categories = json.load(f)
    winners = m.find_winners(winner_data, categories)
    for w in winners:
        winners[w] = winners[w][0]
    for cat in categories:
        if cat not in winners.keys():
            winners[cat] = ""
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    path = 'presenters' + year + '.json'
    with open(path, 'r') as f:
        presenter_data = json.load(f)
    #print(presenter_data)
    fixed = []
    for entry in presenter_data:
        fixed.append(tuple(entry))
    path = 'categories' + year + '.json'
    path = 'gg' + year + 'categories.json' #File with real categories, not really sure if this is right path
    with open(path, 'r') as f:
        real_categories = json.load(f)
    tmp = {}
    presenters = {}
    for cat in real_categories: #format categories to fit with m.present
                                #Note: removed category matching, now only
                                #takes the real categories in dict format
        presenters[cat.lower()] = []                        #{real_cat: real_cat}
        tmp[cat] = cat
    res = m.present(fixed, tmp)

    ##Format results to fit requirements    
   
    for p in res:
        tmp = presenters[p[1]]
        tmp.append(p[0])
        presenters[p[1]] = tmp
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    start = time.time()
    #year = input("Input year >")
    year = '2013'
    dfnom, dfshow, dfhost, dfpresent, dfwin, dfcat = m.init_and_sort(start, year)
    results = {
        "nominees": dfnom,
        "show": dfshow,
        "hosts": dfhost,
        "presenters": dfpresent,
        "winners": dfwin,
        "categories": dfcat
    }
    
    m.store_results(results, year)
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pre_ceremony()
    #year = input("Input year >")
    year = '2013' # Run data initialization and write data to files labeled parsed_data/<category>
    path = 'gg' + year + 'categories.json'
    with open(path, 'r') as f:
        real_categories = json.load(f)
    tmp = {}
    for cat in real_categories: #format categories to fit with m.present
                                #Note: removed category matching, now only
                                #takes the real categories in dict format
                                #{real_cat: real_cat}
        tmp[cat] = cat
    m.main(year, tmp)
    return

if __name__ == '__main__':
    main()
