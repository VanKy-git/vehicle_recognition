import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By

def debug_crawler():
    print("="*60)
    print("🔍 BẮT ĐẦU CHẠY CHẾ ĐỘ DEBUG TÌM LỖI MAGNIFIC")
    print("="*60)
    
    options = EdgeOptions()
    # TỤT QUẦN CLOUDFLARE: TUYỆT ĐỐI KHÔNG DÙNG HEADLESS TRONG LÚC DEBUG
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    try:
        test_url = "https://www.magnific.com/search?format=search&query=car+driving+on+street&page=1"
        print(f"👉 Đang mở URL: {test_url}")
        driver.get(test_url)
        
        print("⏳ Đang chờ 10 giây để mày nhìn xem có bị Cloudflare chặn không...")
        time.sleep(10)
        
        # Cuộn trang một nhịp để kích hoạt DOM
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(3)
        
        # 1. CHỤP ẢNH HIỆN TRƯỜNG
        driver.save_screenshot("debug_screenshot.png")
        print("📸 Đã chụp màn hình lưu vào: debug_screenshot.png")
        
        # 2. LƯU DOM THỰC TẾ
        with open("debug_dom.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 Đã lưu HTML thực tế vào: debug_dom.html")
        
        # 3. MỔ XẺ TOÀN BỘ THẺ IMG TRÊN TRANG
        print("\n🔎 ĐANG QUÉT TOÀN BỘ THẺ <img>...")
        all_imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"Tổng số thẻ <img> tìm thấy: {len(all_imgs)}")
        
        valid_count = 0
        for idx, img in enumerate(all_imgs):
            src = img.get_attribute("src")
            data_src = img.get_attribute("data-src")
            alt = img.get_attribute("alt")
            
            # Chỉ in ra những ảnh có vẻ là ảnh thật (bỏ qua icon, logo svg)
            if src and (".jpg" in src or ".png" in src or "magnific" in src):
                valid_count += 1
                if valid_count <= 5: # In thử 5 ảnh đầu tiên để soi cấu trúc
                    print(f"  [Ảnh {valid_count}] Alt: '{alt}'")
                    print(f"      |- src: {src}")
                    print(f"      |- data-src: {data_src}")
        
        print(f"\n=> Có {valid_count} ảnh khả thi trên tổng {len(all_imgs)} thẻ <img>.")

    except Exception as e:
        print(f"❌ Lỗi văng script: {e}")
    finally:
        print("🛑 Đóng trình duyệt. Hãy kiểm tra Terminal và 2 file debug vừa tạo!")
        driver.quit()

if __name__ == "__main__":
    debug_crawler()