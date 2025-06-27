import requests
import pandas as pd

API_KEY = 'de4d265554f54a1eae00108032004800'
headers = { 'X-Auth-Token': API_KEY }

url = 'https://api.football-data.org/v4/competitions/CL/matches'

response = requests.get(url, headers=headers)
data = response.json()
print(data)