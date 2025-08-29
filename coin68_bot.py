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
        return []
    
    try:
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/gists/{GIST_ID}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            gist_data = response.json()
            content = gist_data['files']['sent_links.json']['content']
            sent_links = json.loads(content)
            print(f"✅ Đã tải {len(sent_links)} link từ Gist")
            return sent_links
        else:
            print(f"❌ Lỗi tải Gist: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Lỗi kết nối đến Gist: {e}")
        return []

def save_sent_links(links):
    """Lưu danh sách các link đã gửi lên GitHub Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("⚠️ GIST_TOKEN hoặc GIST_ID chưa được cấu hình")
        return False
    
    try:
        # Giữ chỉ 500 link gần nhất
        if len(links) > 500:
            links = links[-500:]
        
        # Chuẩn bị data để update Gist
        data = {
            "files": {
                "sent_links.json": {
                    "content": json.dumps(links, ensure_ascii=False, indent=2)
                }
            }
        }
        
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.patch(
            f'https://api.github.com/gists/{GIST_ID}',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Đã lưu {len(links)} link lên Gist")
            return True
        else:
            print(f"❌ Lỗi lưu Gist: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kết nối đến Gist: {e}")
        return False

# Các hàm khác giữ nguyên (get_rss_data, send_telegram_photo, format_caption, etc.)
# ...
