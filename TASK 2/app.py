from flask import Flask, jsonify
from country_service import get_country_data, store_country_data, generate_summary

app = Flask(__name__)

@app.route('/get_country/<country_name>', methods=['GET'])
def get_country(country_name):
    return get_country_data(country_name)

@app.route('/store_country/<country_name>', methods=['GET'])
def store_country(country_name): 
    return store_country_data(country_name)

@app.route('/generate_summary/<country_name>', methods=['GET'])
def generate_country_summary(country_name):
    return generate_summary(country_name)

if __name__ == '__main__':
    app.run(debug=True)
