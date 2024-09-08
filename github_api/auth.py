# auth.py
import os

def get_github_token():
    token = os.getenv('GITHUB_TOKEN_GEN_AI')
    if not token:
        raise ValueError("GITHUB_TOKEN_GEN_AI environment variable is not set")
    return token
