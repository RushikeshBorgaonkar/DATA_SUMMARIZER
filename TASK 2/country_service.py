from db import get_db_connection
from api_client import fetch_country_data_from_api
from groq_client import generate_groq_summary
from flask import jsonify, request
from prompts import population_prompt, gdp_prompt, export_prompt, invalid_prompt 

def get_country_data(country_name):
    data = fetch_country_data_from_api(country_name)
    return jsonify(data)

def store_country_data(country_name):
    print(f"Fetching data for country: {country_name}")
    data = fetch_country_data_from_api(country_name)

    if 'error' not in data:
        data = data[0]  
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
        CREATE TABLE IF NOT EXISTS country_detail (
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
        INSERT INTO country_detail (name, population, capital, currency, region, urban_population, urban_population_growth, exports, gdp, gdp_growth, gdp_per_capita)
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

def generate_summary(country_name):
    conn = get_db_connection()
    cur = conn.cursor()

    print(f"Searching for country: {country_name}")

    select_query = '''
    SELECT name, population, capital, currency, region, urban_population, urban_population_growth, exports, gdp, gdp_growth, gdp_per_capita
    FROM country_detail
    WHERE name ILIKE %s
    '''
    cur.execute(select_query, (country_name,))
    country = cur.fetchone()
    cur.close()
    conn.close()

    if not country:
        return jsonify({'error': 'Country not found'}), 404

    country_data = {
        'name': country[0],
        'population': country[1],
        'capital': country[2],
        'currency': country[3],
        'region': country[4],
        'urban_population': country[5],
        'urban_population_growth': country[6],
        'exports': country[7],
        'gdp': country[8],
        'gdp_growth': country[9],
        'gdp_per_capita': country[10]
    }

    param = request.args.get('param')

    
    if param == 'population':
        prompt = population_prompt(country_data)
    elif param == 'gdp':
        prompt = gdp_prompt(country_data)
    elif param == 'export':
        prompt = export_prompt(country_data)
    else:
        return jsonify({'message': invalid_prompt()})

    summary = generate_groq_summary(prompt).strip()
    return summary
