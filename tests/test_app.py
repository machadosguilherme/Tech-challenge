import json
import pytest
from app import app
import requests
import json


class TestClass:

    def test_get_home_router(self):
        req = requests.get("http://localhost:5000/")
        assert req.status_code == 200

    def test_get_router_production(self):
        req = requests.get("http://localhost:5000/api-v1/production")
        assert req.status_code == 200


    def test_get_data_from_production_router(self):
        req = requests.get("http://localhost:5000/api-v1/production").json()
        assert req['message'] == "Dados da produção"
        assert req['status'] == '200'
        assert req['data'] is not None


    def test_get_all_years_from_production_router(self):
        req = requests.get("http://localhost:5000/api-v1/production").json()
        
        
        



        
        

