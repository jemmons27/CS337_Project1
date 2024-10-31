import json
import re
from collections import Counter
from fuzzywuzzy import fuzz

# Load the JSON data from the file
with open('gg2013.json', 'r') as file:
    data = json.load(file)

# Define the regular expressions
regex_patterns = [
    r'contenders for (Best [\w\s]+)',                      # Match for contenders
    r'Best ([\w\s]+) (in a ([\w\s]+)|goes to|is awarded to [\w\s]+)',  # Match for Best in a category, goes to, or awarded
    r'[\w\s]+ (sweeps the category for|wins at.*?for) (Best [\w\s]+)'  # Match for sweeps the category or wins at
]

# Function to extract and clean categories
def extract_categories(text):
    categories = []
    for pattern in regex_patterns:
        matches = re.findall(pattern, text)
        if matches != []:
            print(matches, pattern)
        for match in matches:
            # If match is a tuple, join its elements into a single string
            if isinstance(match, tuple):
                match = ' in a '.join(match)
            # Clean up the match to remove parts after "goes to" or "is awarded to"
            cleaned_match = re.sub(r'\s+(goes to|is|for).*', '', match)
            # Ensure the category starts with "Best"
            if not cleaned_match.startswith("Best"):
                cleaned_match = "Best " + cleaned_match
            categories.append(cleaned_match)
    return categories

# Extract categories from the dataset and count occurrences
category_counter = Counter()
categories_data = []

for entry in data:
    text = entry.get('text', '')
    categories = extract_categories(text)
    if categories != []:
        print(type(categories))
    if categories:
        categories_data.append({
            'text': text,
            'categories': categories
        })
        category_counter.update(categories)
print(category_counter)
# Convert Counter to a dictionary with string keys
category_counts_dict = {str(key): value for key, value in category_counter.items()}

# Filter out categories with low occurrence counts
threshold = 5  # Set your threshold here
filtered_category_counts = {key: value for key, value in category_counts_dict.items() if value >= threshold}

# Sort the filtered categories by their counts
sorted_filtered_category_counts = sorted(filtered_category_counts.items(), key=lambda item: item[1], reverse=True)

# Function to normalize and merge similar categories
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

# Merge similar categories
merged_category_counts = merge_similar_categories(sorted_filtered_category_counts)

# Convert merged categories to a sorted list
sorted_merged_category_counts = sorted(merged_category_counts.items(), key=lambda item: item[1], reverse=True)

# Save the sorted merged category counts to a JSON file
with open('catres.json', 'w') as file:
    json.dump(sorted_merged_category_counts, file, indent=4)

print("Categories extracted and saved to categorized_data.json")
print("Sorted merged category counts extracted and saved to sorted_merged_category_counts.json")