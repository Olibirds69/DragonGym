import requests

# Expression to compute
expression = "5 * (3 + 7) / 2"

url = "https://api.mathjs.org/v4/"

# Send request with query params
params = {"expr": expression}
response = requests.get(url, params=params)

if response.status_code == 200:
    print(f"Expression: {expression}")
    print(f"Result from API: {response.text}")
else:
    print("Error:", response.status_code, response.text)
