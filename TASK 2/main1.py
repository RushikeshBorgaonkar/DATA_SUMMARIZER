#### Code is un separated with changing prompt. Focusing on the 2 parameters


import requests
import psycopg2
from groq import Groq
import os
from flask import Flask, jsonify

app = Flask(__name__)

API_KEY = "FQkFL3879juP2oqBPkz1gQ==iOaHOGYaKA9guAt6"
api_url = 'https://api.api-ninjas.com/v1/country'

GROQ_API_KEY = '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'

DB_HOST = "localhost"
DB_NAME = "Country_data"
DB_USER = "postgres"
DB_PASS = "admin123"

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

        currency_name = data['currency']['name'] if 'currency' in data else None
        urban_population = data.get('urban_population', 0)
        urban_population_growth = data.get('urban_population_growth', 0)
        exports = data.get('exports', 0)
        gdp = data.get('gdp', 0)
        gdp_growth = data.get('gdp_growth', 0)
        gdp_per_capita = data.get('gdp_per_capita', 0)

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS New_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            population BIGINT,
            capital VARCHAR(100),
            currency VARCHAR(50),
            region VARCHAR(100),
            urban_population BIGINT,
            urban_population_growth BIGINT,
            exports BIGINT,
            gdp BIGINT,
            gdp_growth BIGINT,
            gdp_per_capita BIGINT
        );
        '''
        cur.execute(create_table_query)

      
        insert_query = '''
        INSERT INTO New_table (name, population, capital, currency, region, urban_population, urban_population_growth, exports, gdp, gdp_growth, gdp_per_capita)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(insert_query, (
            data.get('name', None),
            data.get('population', None),
            data.get('capital', None),
            currency_name,
            data.get('region', None),
            urban_population,
            urban_population_growth,
            exports,
            gdp,
            gdp_growth,
            gdp_per_capita
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
    SELECT name, population, capital, currency, region, urban_population, urban_population_growth, exports, gdp, gdp_growth, gdp_per_capita
    FROM New_table
    WHERE name ILIKE %s
    '''
    cur.execute(select_query, (country_name,))
    country = cur.fetchone()
    cur.close()
    conn.close()

    if not country:
        print("Country not found in database.")  
        return jsonify({'error': 'Country not found'}), 404  

    # Format the retrieved data for summary generation
    data = (f"Country: {country[0]}, Population: {country[1]}, Capital: {country[2]}, Currency: {country[3]}, "
            f"Region: {country[4]}, Urban Population: {country[5]}, Urban Population Growth: {country[6]}, "
            f"Exports: {country[7]}, GDP: {country[8]}, GDP Growth: {country[9]}, GDP per Capita: {country[10]}")

    prompt = f"You are a insightful data analyst and gives summaries on the given information . You give a precise and clear understandable information.: {data}."

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

    summary = chat_completion.choices[0].message.content.strip()
    summary = summary.replace("**"," ")
    return summary  

if __name__ == '__main__':
    app.run(debug=True)
