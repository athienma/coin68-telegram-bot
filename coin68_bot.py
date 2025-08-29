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

# Cấu hình
MAX_NEWS_PER_RUN = 10
DELAY_BETWEEN_MESSAGES = 2  # Giây giữa các tin

def debug_env():
    """Debug environment variables"""
    print("🔍 DEBUG ENVIRONMENT VARIABLES:")
    print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'}")
    print(f"CHAT_ID: {'SET' if CHAT_ID else 'MISSING'}")
    print(f"Python Version: {sys.version}")
    print(f"Max news per run: {MAX_NEWS_PER_RUN}")
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
        
        if response.status_code != 200:
            print(f"❌ Lỗi HTTP: {response.status_code}")
            return None
            
        # Parse XML
        try:
            root = ET.fromstring(response.content)
            print("✅ Parse XML thành công")
        except ET.ParseError as e:
            print(f"❌ Lỗi parse XML: {e}")
            return None
            
        news_items = []
        for item in root.findall('.//item'):
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                
                title = title_elem.text if title_elem is not None else "Không có tiêu đề"
                link = link_elem.text if link_elem is not None else "#"
                pub_date = pub_date_elem.text if pub_date_elem is not None else ""
                
                # Chuyển đổi pub_date thành datetime object để sắp xếp
                try:
                    pub_date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    pub_date_obj = datetime.now()
                
                news_items.append({
                    'title': title,
                    'link': link, 
                    'pub_date_obj': pub_date_obj
                })
                
            except Exception as e:
                print(f"⚠️ Lỗi xử lý item: {e}")
                continue
        
        # Sắp xếp tin theo thời gian (mới nhất trước)
        news_items.sort(key=lambda x: x['pub_date_obj'], reverse=True)
        
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

def send_telegram_message(message):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            return False
            
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        return result.get('ok', False)
            
    except Exception as e:
        print(f"❌ Lỗi gửi tin nhắn: {e}")
        return False

def load_sent_links():
    """Tải danh sách các link đã gửi"""
    try:
        with open('sent_links.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_sent_links(links):
    """Lưu danh sách các link đã gửi"""
    try:
        # Giữ chỉ 500 link gần nhất
        if len(links) > 500:
            links = links[-500:]
        
        with open('sent_links.json', 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Lỗi lưu sent_links: {e}")

def main():
    print("=" * 60)
    print("🤖 Bắt đầu Coin68 Telegram Bot - SIMPLIFIED VERSION")
    print("=" * 60)
    
    debug_env()
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ERROR: Thiếu BOT_TOKEN hoặc CHAT_ID")
        sys.exit(1)
    
    # Tải danh sách đã gửi
    sent_links = load_sent_links()
    print(f"📋 Số tin đã gửi trước đây: {len(sent_links)}")
    
    # Lấy dữ liệu RSS
    news_items = get_rss_data()
    if not news_items:
        print("❌ Không có dữ liệu RSS")
        sys.exit(1)
    
    # Lọc tin chưa gửi
    new_items = [item for item in news_items if item['link'] not in sent_links]
    print(f"📨 Số tin mới: {len(new_items)}")
    
    if not new_items:
        print("✅ Không có tin mới")
        sys.exit(0)
    
    # Giới hạn số tin gửi mỗi lần
    items_to_send = new_items[:MAX_NEWS_PER_RUN]
    print(f"📤 Sẽ gửi {len(items_to_send)} tin")
    
    # Gửi tin - CHỈ GỬI LINK
    success_count = 0
    for i, item in enumerate(items_to_send):
        try:
            print(f"\n📨 Đang gửi tin {i+1}/{len(items_to_send)}...")
            
            # CHỈ GỬI LINK - Telegram tự động tạo preview
            message = item['link']
            
            # Gửi tin nhắn
            if send_telegram_message(message):
                sent_links.append(item['link'])
                success_count += 1
                print(f"✅ Tin {i+1} gửi thành công")
            else:
                print(f"❌ Tin {i+1} gửi thất bại")
            
            # Chờ giữa các tin
            if i < len(items_to_send) - 1:
                import time
                time.sleep(DELAY_BETWEEN_MESSAGES)
                
        except Exception as e:
            print(f"❌ Lỗi khi gửi tin {i+1}: {e}")
    
    # Lưu danh sách đã gửi
    save_sent_links(sent_links)
    
    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH! Đã gửi {success_count}/{len(items_to_send)} tin mới")
    print(f"💾 Tổng số tin đã gửi: {len(sent_links)}")
    print("=" * 60)
    
    if success_count == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
