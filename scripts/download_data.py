import os
import time
import requests
import urllib.parse 
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. KHAI BÁO KEYWORD ĐA DẠNG
VEHICLE_CLASSES = {
    "car": ["car driving on road", "parked car street", "car traffic jam"],
    "motorcycle": ["motorcycle riding", "motorbike parked", "sport motorcycle"],
    "bus": ["city bus", "school bus", "tourist bus"],
    "truck": ["cargo truck", "delivery truck", "dump truck"],
    "bicycle": ["bicycle riding", "mountain bike", "bicycle parked street"],
    "ambulance": ["ambulance driving", "ambulance emergency", "hospital ambulance"],
    "police_car": ["police car driving", "police cruiser", "police car night"],
    "taxi": ["yellow taxi", "taxi driving street", "taxi waiting"],
    "tractor": ["farm tractor", "tractor field", "agricultural tractor"],
    "boat": ["boat on water", "fishing boat", "speedboat"]
}

SCRIPT_DIR = Path(__file__).parent.parent 
BASE_DIR = str(SCRIPT_DIR / "data" / "raw")
os.makedirs(BASE_DIR, exist_ok=True)
IMAGES_PER_CLASS = 5000 

def download_image(url, save_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.freepik.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

def crawl_freepik(class_name, keywords_list, target_count):
    print(f"\n{'='*50}")
    print(f"🚀 BẮT ĐẦU CRAWL LỚP: [{class_name.upper()}]")
    print(f"{'='*50}")
    
    class_dir = os.path.join(BASE_DIR, class_name)
    os.makedirs(class_dir, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    # Bỏ comment dòng dưới nếu em không muốn nó hiện cửa sổ Chrome lên làm phiền
    # options.add_argument('--headless') 
    
    driver = webdriver.Chrome(options=options)
    downloaded_count = 0
    
    try:
        count_per_keyword = target_count // len(keywords_list)
        
        for kw_idx, keyword in enumerate(keywords_list):
            if downloaded_count >= target_count: break
            
            print(f"\n▶️ [{class_name}] Đang quét Keyword {kw_idx + 1}/{len(keywords_list)}: '{keyword}'...")
            
            safe_keyword = urllib.parse.quote_plus(keyword)
            search_url = f"https://www.freepik.com/search?format=search&query={safe_keyword}&type=photo"
            
            driver.get(search_url)
            
            # Click Cookie
            try:
                accept_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                accept_btn.click()
                time.sleep(1)
            except Exception:
                pass
            
            try:
                driver.execute_script("document.body.style.overflow = 'auto';")
            except Exception:
                pass

            kw_downloaded = 0
            page_scrolls = 0
            empty_scrolls = 0 
            
            while kw_downloaded < count_per_keyword and page_scrolls < 100:
                images = driver.find_elements(By.CSS_SELECTOR, "img")
                
                new_downloads_in_scroll = 0
                for img in images:
                    if kw_downloaded >= count_per_keyword or downloaded_count >= target_count:
                        break

                    # Ưu tiên lấy ảnh từ src, nếu bị lazy-load thì lấy data-src hoặc srcset
                    img_url = img.get_attribute("src")
                    if not img_url or img_url.startswith("data:image"):
                        img_url = img.get_attribute("data-src")
                    if not img_url or img_url.startswith("data:image"):
                        srcset = img.get_attribute("srcset")
                        if srcset:
                            img_url = srcset.split(",")[0].split(" ")[0]

                    # [CHÌA KHÓA VÀNG Ở ĐÂY]: Thêm "magnific.com" vào bộ lọc
                    if img_url and ("magnific.com" in img_url or "freepik" in img_url or "ftcdn" in img_url) and ("avatar" not in img_url and "logo" not in img_url):
                        # Cắt bỏ phần tham số lằng nhằng phía sau đuôi .jpg (nếu có) để tên file sạch sẽ hơn
                        clean_url = img_url.split("?")[0] if "?" in img_url else img_url
                        
                        save_path = os.path.join(class_dir, f"{class_name}_{downloaded_count}.jpg")

                        if not os.path.exists(save_path):
                            if download_image(clean_url, save_path):
                                downloaded_count += 1
                                kw_downloaded += 1
                                new_downloads_in_scroll += 1

                                # Cứ mỗi 20 ảnh báo cáo 1 lần cho xôm tụ
                                if downloaded_count % 20 == 0:
                                    print(f"  [LOG] Đã tải {downloaded_count}/{target_count} ảnh")
                
                # Cuộn chuột dứt khoát 1 khung hình
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(3.5) # Chờ xíu cho ảnh bung ra
                page_scrolls += 1
                
                if new_downloads_in_scroll == 0:
                    empty_scrolls += 1
                    if empty_scrolls >= 3:
                        print(f"  [CẢNH BÁO] Hết ảnh mới. Chuyển từ khóa khác...")
                        break
                else:
                    empty_scrolls = 0
                    
            print(f"✅ Xong từ khóa '{keyword}'. Thu được: {kw_downloaded} ảnh.")
            
    except Exception as e:
        print(f"\n[LỖI SẬP SCRIPT] Đứt gánh tại lớp {class_name}: {e}")

    finally:
        driver.quit()
        print(f"[CLEANUP] Đã đóng cửa sổ Chrome an toàn cho lớp [{class_name.upper()}].")

    print(f"\n🎉 HOÀN THÀNH LỚP [{class_name.upper()}]: Tổng thu được {downloaded_count} ảnh.")

if __name__ == "__main__":
    print("AUTO CRAWL DATA")
    for class_name, keywords_list in VEHICLE_CLASSES.items():
        crawl_freepik(class_name, keywords_list, IMAGES_PER_CLASS)