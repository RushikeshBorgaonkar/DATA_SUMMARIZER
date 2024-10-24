import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
api_url = os.getenv("api_url")

def fetch_country_data_from_api(country_name):
    headers = {'X-Api-Key': API_KEY}
    params = {'name': country_name}
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {'error': response.status_code, 'message': response.text}
