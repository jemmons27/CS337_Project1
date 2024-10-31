# CS337_Project1

Steps for editing combined.py:
Add any regex patterns for extracting relevant tweets into the patterns dict
in init(regex) in the form '<function>: [compiled patterns]' where function is
what the extracted tweets will be used for

Any edits having to do with grabbing a subset of tweets from the original dataset
happen in init_and_sort(). 

More than likely the edits should happen around inside of the loop
around line 230, which loops through an array of all tweets and checks the tweets against all
sets of patterns, before grabbing all matches and sorting them according to what set of patterns (the key of the patterns dict) grabbed the matches.

At the end of the function, you should have a np.array of U500 (unsigned char(500)) matches,
sometimes tuples will be found and that is ok but know that the loop over range(len(curr)) will
error out if re.sub() is called on a tuple, so handle it before then

make sure you are returning a dataframe with only the matches you need for one function and add it to the return statement at the end of init_and_sort(), as well as call it in main()

Last step is to add a new function taking the dataframe. 


        

Find categories
Find potential winners
Find fashion/parties

match winners, nominees, presenters to categories

format results and returns

possible runtime or accuracy optimization

categories(Find categories) -> winners (find possible winners and try to match them with categories)
                                nominees matching with categories

                                edit presenters to match with categories
                                edit nominees to match with categories
                                edit winners to match with categories

                                return/format results