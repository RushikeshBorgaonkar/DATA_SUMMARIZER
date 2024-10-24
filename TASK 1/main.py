import requests
import psycopg2
from groq import Groq
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


API_KEY = os.getenv("API_KEY")
api_url = os.getenv("api_url")


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_db_connection():
    conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=5432
        )
    return conn

@app.route('/get_country/<country_name>', methods=['GET'])
def get_country_data(country_name):
    headers = {'X-Api-Key': API_KEY}
    params = {'name': country_name}
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({'error': response.status_code, 'message': response.text})

@app.route('/store_country/<country_name>', methods=['GET'])
def store_country_data(country_name): 
   
        print(f"Fetching data for country: {country_name}")

        headers = {'X-Api-Key': API_KEY}
        params = {'name': country_name}
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()[0]  
            print(f"Data retrieved for {country_name}: {data}")

            conn = get_db_connection()  
            cur = conn.cursor()

            currency_name = data['currency']['name']

            create_table_query = '''
            CREATE TABLE IF NOT EXISTS country (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                population BIGINT,
                capital VARCHAR(100),
                currency VARCHAR(50),
                region VARCHAR(100)
            );
            '''
            cur.execute(create_table_query)

            insert_query = '''
            INSERT INTO country (name, population, capital, currency, region)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cur.execute(insert_query, (
                data['name'], 
                data['population'], 
                data['capital'], 
                currency_name, 
                data['region']
            ))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({'message': 'Country data stored successfully!'})

      


@app.route('/generate_summary/<country_name>', methods=['GET'])
def generate_summary(country_name):
    
        conn = get_db_connection()
        cur = conn.cursor()

        print(f"Searching for country: {country_name}")

       
        select_query = '''
        SELECT name, population, capital, currency, region
        FROM country
        WHERE name ILIKE %s
        '''
        cur.execute(select_query, (country_name,))
        country = cur.fetchone()
        cur.close()
        conn.close()

        if not country:
            print("Country not found in database.")  
            return jsonify({'error': 'Country not found'}), 404  

        
        data = f"Country: {country[0]}, Population: {country[1]}, Capital: {country[2]}, Currency: {country[3]}, Region: {country[4]}"
        prompt = f"Summarize the country data in a detailed paragraph for different countries: {data}."

       
        client = Groq(
            api_key=GROQ_API_KEY
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

       
        summary = chat_completion.choices[0].message.content.strip()  # Ensure the summary is stripped of any whitespace

        return summary  

   
        
if __name__ == '__main__':
    app.run(debug=True)