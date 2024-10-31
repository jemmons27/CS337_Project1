import json

# Load the JSON data from the file
with open('/Users/jasminemeyer/CS337_Project1/party_analysis_results.json', 'r') as file:
    results = json.load(file)

party_mentions = results['party_mentions']
party_avg_sentiment = results['party_avg_sentiment']

# Calculate the overall average sentiment
total_sentiment = sum(party_avg_sentiment.values())
num_parties = len(party_avg_sentiment)
overall_avg_sentiment = total_sentiment / num_parties

# Determine if the overall sentiment is positive or negative
overall_sentiment = 'positive' if overall_avg_sentiment > 0 else 'negative'

# Find the party with the highest mentions
most_mentioned_party = max(party_mentions, key=party_mentions.get)
most_mentions = party_mentions[most_mentioned_party]

# Find the party with the highest average sentiment
highest_sentiment_party = max(party_avg_sentiment, key=party_avg_sentiment.get)
highest_sentiment = party_avg_sentiment[highest_sentiment_party]

# Print the results
print(f"Overall average sentiment is {overall_sentiment} with a score of {overall_avg_sentiment:.2f}")
print(f"Party with the highest mentions: {most_mentioned_party} ({most_mentions} mentions)")