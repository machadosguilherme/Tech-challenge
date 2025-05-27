from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.production import *
import os
from dotenv import load_dotenv
import pandas as pd
from aux_functions import aux_functions
from fastapi.responses import JSONResponse as jsonify

load_dotenv()

# Carregar variáveis de ambiente
ENV = os.getenv('ENV')
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')

app = FastAPI(
    title='Embrapa Vitivinicultura API',
    description='API para consulta de dados de vitivinicultura da Embrapa',
    version="0.1.0"

)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Vitivinicultura da Embrapa"}

@app.get("/production/",
         response_model=ProductionResponse,
         responses={
             200: {
                 "description": "Dados de produção por ano",
                 "model": ProductionResponse
             },
             400: {
                 "description": "Ano não encontrado",
                 "model": ErrorResponse
             }
         })
def get_production(query: ProductionYearQuery = Depends()):
    """
    Consulta de dados de produção
    Parâmetros opcional:
    - ano: int (ex: 2023)
    """

    if ENV == 'LOCAL':
        #Read the file from data folder
        with open('data/Producao.csv', 'r') as file:
            data = pd.read_csv('data/Producao.csv', sep=';')            
        #Convert to json
        result = data.to_dict(orient='records')
        result = aux_functions.convert_data_to_api(result)
            
        return ProductionResponse(
            message="Dados da produção",
            data=result,
            year=query.year
        )
    
    if ENV == 'PROD':

        if query.year is None:
            data = aux_functions.get_production_data()

            return ProductionResponse(
                message="Dados da produção",
                data=data,
                year=None                                
            )            

        else:
            data = aux_functions.get_production_data_per_year(query.year)
            
            return ProductionResponse(
                message=f"Dados da produção para o ano {query.year}",
                data=data,
                year=query.year
            )
        
    



@app.get("/processamento/")
def get_processamento(ano: int = None):
    """
    Consulta de dados de processamento
    """
    #Logica 

@app.get("/comercializacao/")
def get_comercializacao(ano: int = None):
    """
    Consulta de dados de comercializacao
    """
    #Logica 

@app.get("/importacao/")
def get_importacao(ano: int = None):
    """
    Consulta de dados de importacao
    """
    #Logica 

@app.get("/exportacao/")
def get_exportacao(ano: int = None):
    """
    Consulta de dados de exportacao
    """
    #Logica 

