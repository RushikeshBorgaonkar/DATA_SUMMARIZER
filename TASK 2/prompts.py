# You are an insightful data analyst, tasked with summarizing country information in a detailed and informative manner. Your focus should be on key factors like population size, GDP, and related economic indicators. Given the following data, generate a clear, concise summary that highlights these important aspects:


def population_prompt(country_data):
    return (f'''
            You are an insightful data analyst, tasked with summarizing country information in a detailed and informative manner
            .Summarize the population details for {country_data['name']}. 
            It has a population of {country_data['population']} with a urban population of {country_data['urban_population'] }
            and with a urban_population_growth of {country_data['urban_population_growth']}.
            
            ''')

def gdp_prompt(country_data):
    return (f'''
            You are an insightful data analyst, tasked with summarizing country information in a detailed and informative manner
            Provide an economic summary for {country_data['name']}. 
            The country has a GDP of {country_data['gdp']} with a growth rate of {country_data['gdp_growth']}%. "
            The GDP per capita is {country_data['gdp_per_capita']}.''')

def export_prompt(country_data):
    return (f'''
             You are an insightful data analyst, tasked with summarizing country information in a detailed and informative manner
            Summarize the export status for {country_data['name']}. 
            The country exported goods worth {country_data['exports']} last year.''')

def invalid_prompt():
    return "The requested parameter is not available. Please choose either 'population', 'gdp', or 'export'."
