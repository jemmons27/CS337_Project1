import re

def regex_splitting(string, regex):
    match = re.findall(regex, string)
    actor = match[0]
    award = match[1]

def all_candidate_strings(award):
    current_string = ""
    result = []
    words = award.split(" ")
    for i in words:
        current_string = current_string + i + " "
        result.append(current_string)
    return result

print(all_candidate_strings("best support actress #GoldenGlobes"))







