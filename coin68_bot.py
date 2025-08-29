import requests
import xml.etree.ElementTree as ET
import re
import json
import os
import sys
from datetime import datetime

# Lấy token từ environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GIST_TOKEN = os.getenv('GIST_TOKEN')
GIST_ID = os.getenv('GIST_ID')

# Cấu hình
MAX_NEWS_PER_RUN = 10
DELAY_BETWEEN_MESSAGES = 2

def load_sent_links():
    """Tải danh sách các link đã gửi từ GitHub Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("⚠️ GIST_TOKEN hoặc GIST_ID chưa được cấu hình")
        print(f"GIST_TOKEN: {'SET' if GIST_TOKEN else 'MISSING'}")
        print(f"GIST_ID: {'SET' if GIST_ID else 'MISSING'}")
        return []
    
    try:
        print(f"🔗 Đang kết nối đến Gist: {GIST_ID}")
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/gists/{GIST_ID}',
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Gist response status: {response.status_code}")
        
        if response.status_code == 200:
            gist_data = response.json()
            content = gist_data['files']['sent_links.json']['content']
            sent_links = json.loads(content)
            print(f"✅ Đã tải {len(sent_links)} link từ Gist")
            return sent_links
        else:
            print(f"❌ Lỗi tải Gist: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Lỗi kết nối đến Gist: {e}")
        import traceback
        traceback.print_exc()
        return []

# ... (các hàm khác giữ nguyên)
