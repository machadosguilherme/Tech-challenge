from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pandas as pd
import json
from aux_functions import aux_functions

#Importar o arquivo .env
load_dotenv()

#Pegar o valor da variável de ambiente
env = os.getenv('ENV')
host = os.getenv('HOST')
port = os.getenv('PORT')
app = Flask(__name__)
CORS(app)

version = 'v1'

@app.route('/')
def home():
    return jsonify({
        "message": "Bem-vindo à API Flask!",
        "status": "200"
    })

@app.route(f'/api-{version}/production')
def production():

    if env == 'LOCAL':
        #Read the file from data folder
        with open('data/Producao.csv', 'r') as file:
            data = pd.read_csv('data/Producao.csv', sep=';')            
        #Convert to json
        result = data.to_dict(orient='records')
        result = aux_functions.transformar_dados(result)
            
            
        return jsonify({
            "message": "Dados da produção",
            "data": result,
            'status': '200'
        })
    
    if env == 'PROD':
        return jsonify({
            "message": "Bem-vindo à rota de Produção",
            "status": "200"
        })


if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)