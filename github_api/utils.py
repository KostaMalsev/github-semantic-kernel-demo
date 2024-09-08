import base64
import requests

def encode_content(content):
    return base64.b64encode(content.encode("utf-8")).decode("utf-8")

def make_github_request(method, url, headers, data=None):
    response = requests.request(method, url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()