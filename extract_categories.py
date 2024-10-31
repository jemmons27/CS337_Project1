import json

def load_award_categories(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Extract the award categories
    award_categories = list(data.get("award_data", {}).keys())
    return award_categories

# Example usage:
file_path = "/Users/jasminemeyer/CS337_Project1/gg2013answers.json"
award_categories = load_award_categories(file_path)
print(award_categories)