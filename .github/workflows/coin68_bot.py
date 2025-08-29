import requests
import xml.etree.ElementTree as ET
import re
import json
import os
from datetime import datetime

# Lấy token từ environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_rss_data():
    try:
        print("🔄 Đang kết nối đến Coin68 RSS...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/xml, text/xml, */*'
        }
        
        response = requests.get('https://coin68.com/rss/tin-moi-nhat.rss', 
                              headers=headers, timeout=15)
        response.raise_for_status()
        
        print("✅ Đã nhận dữ liệu RSS")
        root = ET.fromstring(response.content)
        namespaces = {'media': 'http://search.yahoo.com/mrss/'}
        
        news_items = []
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            desc_elem = item.find('description')
            link_elem = item.find('link')
            
            title = title_elem.text if title_elem else "Không có tiêu đề"
            description = desc_elem.text if desc_elem else "Không có mô tả"
            link = link_elem.text if link_elem else "#"
            
            # Lấy ảnh từ media content
            image_url = None
            media_content = item.find('media:content', namespaces)
            if media_content is not None:
                image_url = media_content.get('url')
            
            # Làm sạch mô tả
            clean_description = re.sub('<[^<]+?>', '', description)
            clean_description = clean_description.strip()
            
            news_items.append({
                'title': title, 
                'description': clean_description,
                'link': link, 
                'image_url': image_url
            })
        
        print(f"✅ Đã lấy được {len(news_items)} tin")
        return news_items
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy RSS: {e}")
        return None

def send_telegram_message(message, image_url=None):
    try:
        if image_url:
            # Kiểm tra URL ảnh
            try:
                img_response = requests.head(image_url, timeout=5)
                if img_response.status_code != 200:
                    image_url = None
                    print("⚠️ URL ảnh không hợp lệ")
            except:
                image_url = None
        
        if image_url:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            data = {
                "chat_id": CHAT_ID,
                "caption": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, files={"photo": image_url})
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
        
        result = response.json()
        if result.get('ok'):
            return True
        else:
            print(f"❌ Lỗi Telegram: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi gửi tin nhắn: {e}")
        return False

def main():
    print("🤖 Bắt đầu Coin68 Telegram Bot")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Thiếu BOT_TOKEN hoặc CHAT_ID")
        return
    
    # Lấy dữ liệu RSS
    news_items = get_rss_data()
    if not news_items:
        print("❌ Không có dữ liệu để gửi")
        return
    
    # Chỉ gửi 3 tin mới nhất
    for i, item in enumerate(news_items[:3]):
        try:
            # Format tin nhắn
            description = item['description']
            if len(description) > 250:
                description = description[:250] + "..."
            
            message = f"<b>{item['title']}</b>\n\n{description}\n\n🔗 <a href='{item['link']}'>Đọc tiếp trên Coin68</a>"
            
            print(f"📨 Đang gửi tin {i+1}: {item['title'][:50]}...")
            
            # Gửi tin nhắn
            if send_telegram_message(message, item['image_url']):
                print("✅ Đã gửi thành công")
            else:
                print("❌ Gửi thất bại")
            
            # Chờ 2 giây giữa các tin
            if i < 2:  # Không chờ sau tin cuối
                import time
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Lỗi khi xử lý tin: {e}")
    
    print("🎉 Hoàn thành!")

if __name__ == "__main__":
    main()
