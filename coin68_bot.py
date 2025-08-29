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

def debug_env():
    """Debug environment variables"""
    print("🔍 DEBUG ENVIRONMENT VARIABLES:")
    print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'}")
    print(f"CHAT_ID: {'SET' if CHAT_ID else 'MISSING'}")
    print(f"Python Version: {sys.version}")
    print("-" * 50)

def get_rss_data():
    try:
        print("🔄 Đang kết nối đến Coin68 RSS...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/xml, text/xml, */*'
        }
        
        response = requests.get(
            'https://coin68.com/rss/tin-moi-nhat.rss', 
            headers=headers, 
            timeout=15
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code != 200:
            print(f"❌ Lỗi HTTP: {response.status_code}")
            print(f"❌ Response: {response.text[:200]}...")
            return None
            
        # Parse XML
        try:
            root = ET.fromstring(response.content)
            print("✅ Parse XML thành công")
        except ET.ParseError as e:
            print(f"❌ Lỗi parse XML: {e}")
            return None
            
        namespaces = {'media': 'http://search.yahoo.com/mrss/'}
        
        news_items = []
        for item in root.findall('.//item'):
            try:
                title_elem = item.find('title')
                desc_elem = item.find('description') 
                link_elem = item.find('link')
                
                title = title_elem.text if title_elem is not None else "Không có tiêu đề"
                description = desc_elem.text if desc_elem is not None else "Không có mô tả"
                link = link_elem.text if link_elem is not None else "#"
                
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
                
            except Exception as e:
                print(f"⚠️ Lỗi xử lý item: {e}")
                continue
        
        print(f"✅ Đã lấy được {len(news_items)} tin")
        return news_items
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_telegram_message(message, image_url=None):
    try:
        if not BOT_TOKEN:
            print("❌ Thiếu BOT_TOKEN")
            return False
        if not CHAT_ID:
            print("❌ Thiếu CHAT_ID") 
            return False
            
        print(f"📤 Đang gửi tin nhắn Telegram...")
        
        # KHÔNG gửi ảnh từ Coin68 (vì lỗi IMAGE_PROCESS_FAILED)
        # Luôn gửi dạng text-only để tránh lỗi
        image_url = None
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        
        print("📝 Gửi tin nhắn text (không ảnh)...")
        response = requests.post(url, data=data)
        
        result = response.json()
        if result.get('ok'):
            print("✅ Gửi Telegram thành công")
            return True
        else:
            error_msg = result.get('description', 'Unknown error')
            print(f"❌ Lỗi Telegram: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi gửi tin nhắn: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🤖 Bắt đầu Coin68 Telegram Bot - TEXT ONLY VERSION")
    print("=" * 60)
    
    # Debug environment
    debug_env()
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ERROR: Thiếu BOT_TOKEN hoặc CHAT_ID")
        print("💡 Vui lòng kiểm tra Secrets trong GitHub Settings")
        sys.exit(1)
    
    # Lấy dữ liệu RSS
    news_items = get_rss_data()
    if not news_items:
        print("❌ Không có dữ liệu RSS")
        sys.exit(1)
    
    print(f"📊 Tổng số tin nhận được: {len(news_items)}")
    
    # Chỉ gửi 3 tin đầu
    success_count = 0
    for i, item in enumerate(news_items[:3]):
        try:
            print(f"\n📨 Đang xử lý tin {i+1}: {item['title'][:50]}...")
            
            # Format tin nhắn
            description = item['description']
            if len(description) > 250:
                description = description[:250] + "..."
            
            # Tạo tin nhắn đẹp hơn
            message = f"🚀 <b>{item['title']}</b>\n\n{description}\n\n📖 <a href='{item['link']}'>Đọc tin đầy đủ trên Coin68</a>"
            
            # Gửi tin nhắn (KHÔNG có ảnh)
            if send_telegram_message(message):
                success_count += 1
                print(f"✅ Tin {i+1} gửi thành công")
            else:
                print(f"❌ Tin {i+1} gửi thất bại")
            
            # Chờ 2 giây giữa các tin
            if i < 2:
                import time
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Lỗi khi xử lý tin {i+1}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🎉 Kết thúc! Đã gửi {success_count}/3 tin thành công")
    print("=" * 60)
    
    if success_count == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
