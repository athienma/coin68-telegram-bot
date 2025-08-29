import requests
import xml.etree.ElementTree as ET
import re
import json
import os
import sys
from datetime import datetime

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GIST_TOKEN = os.getenv('GIST_TOKEN')
GIST_ID = os.getenv('GIST_ID')

# Config
MAX_NEWS_PER_RUN = 10
DELAY_BETWEEN_MESSAGES = 2

def load_sent_links():
    """Load sent links from GitHub Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("GIST_TOKEN or GIST_ID not configured")
        return []
    
    try:
        print(f"Connecting to Gist: {GIST_ID}")
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/gists/{GIST_ID}',
            headers=headers,
            timeout=10
        )
        
        print(f"Gist response status: {response.status_code}")
        
        if response.status_code == 200:
            gist_data = response.json()
            content = gist_data['files']['sent_links.json']['content']
            sent_links = json.loads(content)
            print(f"Loaded {len(sent_links)} links from Gist")
            return sent_links
        else:
            print(f"Error loading Gist: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Gist connection error: {e}")
        return []

# ... (keep other functions in English)
