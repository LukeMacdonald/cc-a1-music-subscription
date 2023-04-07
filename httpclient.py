import os
import requests


class HTTPClient:
    def __init__(self):
        self.base_url = os.environ.get('API_URL')
        self.headers = {'Content-Type': 'application/json'}

    def get(self, path, params):
        url = self.base_url + path
        response = requests.get(url=url, headers=self.headers, params=params)
        return {'status_code': response.status_code, 'body': response.json()}

    def post(self, path, json):
        url = self.base_url + path
        response = requests.post(url, headers=self.headers, json=json)
        return {'status_code': response.status_code, 'body': response.json()}

    def delete(self, path, params):
        url = self.base_url + path
        response = requests.delete(url=url, headers=self.headers, params=params)
        return {'status_code': response.status_code, 'body': response.json()}


client = HTTPClient()