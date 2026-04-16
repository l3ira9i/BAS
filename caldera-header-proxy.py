#!/usr/bin/env python3
import os, json
from flask import Flask, request, Response
import requests

app = Flask(__name__)
CALDERA_URL = os.getenv("CALDERA_URL", "http://caldera:8888")
CALDERA_API_KEY = os.getenv("CALDERA_API_KEY")
PROXY_PORT = int(os.getenv("PROXY_PORT", 8890))

def get_headers():
    headers = {k: v for k, v in request.headers 
               if k.lower() not in ['host', 'connection', 'content-length']}
    if CALDERA_API_KEY:
        headers['KEY'] = CALDERA_API_KEY
    return headers

def forward(target_url, data=None):
    try:
        resp = requests.request(
            method=request.method, url=target_url,
            headers=get_headers(),
            data=data if data else request.get_data(),
            params=request.args, timeout=30, allow_redirects=False)
        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(n, v) for n, v in resp.raw.headers.items() 
                           if n.lower() not in excluded]
        return Response(resp.content, resp.status_code, response_headers)
    except requests.exceptions.RequestException as e:
        return Response(f'{{"error": "{e}"}}', 502, content_type='application/json')

@app.route('/api/v2/abilities', methods=['POST'])
def proxy_abilities_post():
    try:
        body = json.loads(request.get_data())
        # Ajouter un executor fictif si le tableau est vide
        if 'executors' in body and len(body['executors']) == 0:
            body['executors'] = [{
                "name": "sh",
                "platform": "linux", 
                "command": "echo openaev-placeholder"
            }]
        data = json.dumps(body).encode()
    except Exception:
        data = request.get_data()
    return forward(f"{CALDERA_URL}/api/v2/abilities", data=data)

@app.route('/api/v2/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_v2(endpoint):
    return forward(f"{CALDERA_URL}/api/v2/{endpoint}")

@app.route('/plugin/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_plugin(endpoint):
    # Transfère les requêtes destinées aux plugins Caldera
    return forward(f"{CALDERA_URL}/plugin/{endpoint}")
    
@app.route('/api/v1/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_v1(endpoint):
    return forward(f"{CALDERA_URL}/api/v1/{endpoint}")

@app.route('/api/rest', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_rest():
    return forward(f"{CALDERA_URL}/api/rest")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PROXY_PORT)
