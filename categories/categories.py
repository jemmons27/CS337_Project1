import json
import re
from collections import Counter

# Load the JSON data from the file
with open('/Users/jasminemeyer/CS337_Project1/gg2013.json', 'r') as file:
    data = json.load(file)

# Define the regular expressions
regex_patterns = [
    r'contenders for (Best [\w\s]+)',
    r'Best ([\w\s]+) in a ([\w\s]+)',
    r'[\w\s]+ sweeps the category for (Best [\w\s]+)',
    r'Best ([\w\s]+) goes to',
    r'Golden Globes for (Best [\w\s]+) goes to',
    r'Best ([\w\s]+) is awarded/given to [\w\s]+',
    r'[\w\s]+ wins at Golden Globes 2013 for (Best [\w\s]+)'
]

# Function to extract categories
def extract_categories(text):
    categories = []
    for pattern in regex_patterns:
        matches = re.findall(pattern, text)
        categories.extend(matches)
    return categories

# Extract categories from the dataset and count occurrences
category_counter = Counter()
categories_data = []

for entry in data:
    text = entry.get('text', '')
    categories = extract_categories(text)
    if categories:
        categories_data.append({
            'text': text,
            'categories': categories
        })
        category_counter.update(categories)

# Convert Counter to a dictionary with string keys
category_counts_dict = {str(key): value for key, value in category_counter.items()}

# Filter out categories with low occurrence counts
threshold = 5  # Set your threshold here
filtered_category_counts = {key: value for key, value in category_counts_dict.items() if value >= threshold}

# Sort the filtered categories by their counts
sorted_filtered_category_counts = sorted(filtered_category_counts.items(), key=lambda item: item[1], reverse=True)

# Save the sorted filtered category counts to a JSON file
with open('/Users/jasminemeyer/CS337_Project1/categories/sorted_filtered_category_counts.json', 'w') as file:
    json.dump(sorted_filtered_category_counts, file, indent=4)

print("Categories extracted and saved to categorized_data.json")
print("Sorted filtered category counts extracted and saved to sorted_filtered_category_counts.json")