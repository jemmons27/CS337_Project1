# CS337_Project1

        regex which indicate thing
        run regex
        capture group wins -> substring
        Look at substring, see which matches nominee list and keep it (put on list as candidate for winner/increment counter), if not throw away
        Pick majority vote from aggregation

        Dont want to run too many instances of program
        
        Two parameters after knowing award name
            TO find winner of best picture, parameter is best picture, found in

            5-10 regex for winning
    

    Grab Nominees, split on wins, match nominees to awards found, whoever is majority voted is the chosen winner


General Outline:
 - Shared helpers
        Clean text - Case consistency, get rid of extra whitespace, artifacts like links or RTS if not being used
        Load Json - As it sounds
        Format results - Put results into JSON/plaintext scheme specified by assignment
        Compare results to gg2013answers
- initial Parse:
        - Clean tweets on first pass
                -Depending on runtime, we might want to delete all tweets which aren't useful for our regex
                patterns or other search criteria
        - Grab potential nominees, hosts, award names/categories, presenters, special 
                -Loop through list of regex patterns for nominees, hosts, award show name, etc individually
                        -For this, we can implement functionality checking if multiple patterns are true (i.e. if x is in award categories it likely includes a nominee or winner as well) in the event of runtime concerns
        - From nominees and award names, find winners and link nominees to categories
        - Take results and run them through JSON formatting function for final results

- Setting up the shared code
        - For our initial version of the shared code, it might be easiest to run all of our functions separately (i.e
        not finding nominees and award categories in the same pass through the dataset) to get a baseline on runtime
        - Possible combinable functions: Find nominees, award categories, hosts, fashion/performances/extra, award show name
        - Requires nominees and/or categories - winners, matching nominees to presenters
                - This would have to be on a second pass through the dataset, but to speed up we could remove now irrelevant tweets
        

