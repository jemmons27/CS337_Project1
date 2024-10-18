# import re

# # Example patterns for Presenters, Nominees, and Winners
# patterns = {
#     'presenter': [
#         r"([A-Za-z\s]+)\s+introduces\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+presents\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+announces\s+(best\s+\w+(?:\s\w+)*)"
#     ],
#     'nominee': [
#         r"([A-Za-z\s]+)\s+loses\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+was\s+nominated\s+for\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+deserved\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+didn't\s+get\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+should\s+have\s+won\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+robbed"
#     ],
#     'winner': [
#         r"([A-Za-z\s]+)\s+wins\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+takes\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+gets\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+receives\s+(best\s+\w+(?:\s\w+)*)",
#         r"([A-Za-z\s]+)\s+sweeps\s+the\s+category\s+for\s+(best\s+\w+(?:\s\w+)*)",
#         r"best\s+(\w+)\s+in\s+a\s+(\w+)\s+goes\s+to\s+([A-Za-z\s]+)",
#         r"([A-Za-z\s]+)\s+wins\s+at\s+golden\s+globes\s+\d+\s+for\s+(best\s+\w+(?:\s\w+)*)",
#         r"best\s+(\w+)\s*:\s*([A-Za-z\s]+)",
#         r"best\s+(\w+)\s+is\s+(?:awarded|given)\s+to\s+([A-Za-z\s]+)"
# 	],
# 	'host': [
# 		r"([A-Za-z\s]+)\s+hosts?\b",
# 		r"([A-Za-z\s]+)\.\.\.\s*hosting\b",
# 		r"([A-Za-z\s]+)\s+kicks\s+off\b",
# 		r"Hosts?\s+([A-Za-z\s]+)",
# 		r"([A-Za-z\s]+)\s+hosted\b",
# 		r"hosted by\s+([A-Za-z\s]+)\b"
# 	]
# }