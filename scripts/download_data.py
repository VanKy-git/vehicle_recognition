"""
=============================================================
  MAGNIFIC / FREEPIK — IMAGE CRAWLER v5.0
  Hỗ trợ 2 chế độ hoạt động:

  ┌─────────────────────────────────────────────────────────┐
  │  CHẾ ĐỘ 1 — API MODE  (khuyến nghị)                    │
  │  Kích hoạt khi đặt biến môi trường:                     │
  │      set MAGNIFIC_API_KEY=your_key_here  (Windows)      │
  │      export MAGNIFIC_API_KEY=your_key   (Linux/Mac)     │
  │                                                         │
  │  • Không cần Selenium / trình duyệt                     │
  │  • Không cần đăng nhập                                  │
  │  • 100 ảnh/request × tối đa 100 trang = 10,000/keyword  │
  │  • Download song song 12 luồng                         │
  │  • Có rate-limit theo account/IP; xem docs Magnific     │
  │  ⚠️  Lấy API key miễn phí tại: magnific.com/api         │
  │  ⚠️  Kiểm tra license/ToS trước khi dùng ảnh để train.  │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │  CHẾ ĐỘ 2 — SELENIUM MODE  (fallback, không cần key)   │
  │                                                         │
  │  • Dùng Edge browser giống v4 trước                     │
  │  • Download song song 12 luồng (mới)                    │
  │  • Giảm thời gian chờ xuống còn ~60% so với v4          │
  │  • ~40 ảnh/trang × ~20 trang = ~800/keyword             │
  │  → Cần 7+ keyword/class để đủ 5000 ảnh                  │
  └─────────────────────────────────────────────────────────┘

  CÁCH DÙNG:
    python download_data.py

  GIẢI THÍCH TẠI SAO CÁO BỊ ~800 ẢNH/KEYWORD (CHỨA ĐỂ TÌM HIỂU):
    - Web UI Magnific giới hạn pagination thực tế ở trang 20-25
    - 40 ảnh/trang × 20 trang = 800 ảnh → hợp lý
    - Sau trang 20-25: kết quả lặp hoặc trống → code dừng đúng
    - Giải pháp: thêm keyword đa dạng hơn (đã mở rộng trong file này)
=============================================================
"""

import os
import time
import hashlib
import requests
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from io import BytesIO
from PIL import Image

# ============================================================
# API MODE IMPORTS (Selenium chỉ import khi cần)
# ============================================================
MAGNIFIC_API_KEY = (
    os.environ.get("MAGNIFIC_API_KEY", "").strip()
    or os.environ.get("FREEPIK_API_KEY", "").strip()  # backward-compatible env name
)
USE_API_MODE = bool(MAGNIFIC_API_KEY)

if not USE_API_MODE:
    from selenium import webdriver
    from selenium.common.exceptions import (
        InvalidSessionIdException, TimeoutException, WebDriverException
    )
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# CẤU HÌNH — chỉnh sửa ở đây
# ============================================================
VEHICLE_CLASSES = {
    "car": [
        "real car on road photo",
        "passenger car traffic real image",
        "car side view real photo",
        "car front view real photo",
        "car rear view real photo",
        "sedan driving on highway",
        "compact car urban street",
        "car in traffic real image",
        "white sedan real photo",
        "black car road photo",
        "red car street real image",
        "car parked roadside real photo",
        "car daylight outdoor image",
        "car natural lighting photo",
        "commuter car city traffic",
        "realistic car street scene",
        "car intersection traffic image",
        "car highway driving real photo",
        "small passenger car road",
        "real vehicle car photo",
    ],

    "motorcycle": [
        "real motorcycle on road",
        "motorcycle traffic real photo",
        "motorbike side view real image",
        "motorcycle front view real photo",
        "motorcycle rear view road image",
        "scooter driving city street",
        "motorbike rider traffic photo",
        "sport motorcycle highway real image",
        "delivery scooter road photo",
        "motorcycle parked roadside",
        "motorcycle urban traffic image",
        "realistic motorcycle street scene",
        "black motorcycle real photo",
        "white scooter traffic image",
        "motorcycle daylight outdoor photo",
        "motorbike natural lighting image",
        "motorcycle city commute",
        "motorcycle highway driving photo",
        "real motorcycle road scene",
        "motorbike street real photo",
    ],

    "bicycle": [
        "real bicycle on road",
        "bicycle traffic real photo",
        "bike side view real image",
        "bicycle front view real photo",
        "bicycle rear view road image",
        "cyclist riding city street",
        "road bicycle traffic photo",
        "mountain bike urban road",
        "bicycle parked roadside",
        "commuter bicycle real image",
        "bike lane traffic real photo",
        "cycling urban street image",
        "realistic bicycle street scene",
        "bicycle daylight outdoor photo",
        "bicycle natural lighting image",
        "people cycling road real photo",
        "city bike traffic image",
        "bicycle intersection real photo",
        "road bike rider street",
        "real bicycle road scene",
    ],

    "pickup_truck": [
        "real pickup truck on road photo",
        "pickup truck traffic real image",
        "pickup truck side view real photo",
        "pickup truck front view real photo",
        "pickup truck rear view real photo",
        "pickup truck driving on highway",
        "pickup truck parked on street",
        "double cab pickup truck real photo",
        "single cab pickup truck real photo",
        "white pickup truck road photo",
        "black pickup truck traffic photo",
        "red pickup truck real street photo",
        "pickup truck urban road",
        "pickup truck highway traffic",
        "pickup truck daylight real photo",
        "pickup truck city driving",
        "pickup truck outdoors real image",
        "pickup truck in traffic real photo",
        "pickup truck natural lighting photo",
        "pickup truck realistic street scene",
    ],

    "bus": [
        "real city bus on road",
        "public bus traffic real photo",
        "bus side view real image",
        "bus front view real photo",
        "bus rear view real photo",
        "urban transit bus real photo",
        "city bus driving street",
        "bus in traffic real image",
        "coach bus highway real photo",
        "school bus road real photo",
        "electric bus street real image",
        "double decker bus real photo",
        "white bus road photo",
        "yellow bus traffic photo",
        "public transport bus real photo",
        "bus stopped at bus stop",
        "bus driving in city traffic",
        "real passenger bus highway",
        "bus daylight outdoor photo",
        "bus natural street scene",
    ],

    "truck": [
        "cargo truck real road photo",
        "delivery truck driving real image",
        "semi truck highway real photo",
        "heavy truck traffic real photo",
        "box truck urban road photo",
        "truck side view real photo",
        "truck front view real image",
        "truck rear view road photo",
        "freight truck highway image",
        "lorry driving street real photo",
        "transport truck road real photo",
        "cargo truck traffic image",
        "white truck road real photo",
        "commercial truck driving photo",
        "truck parked roadside real image",
        "large truck on highway",
        "realistic truck traffic scene",
        "truck daylight outdoor photo",
        "truck natural lighting road",
        "heavy duty truck real image",
    ],

    "van": [
        "delivery van real road photo",
        "cargo van traffic real image",
        "passenger van street real photo",
        "van side view real photo",
        "van front view real image",
        "van rear view road photo",
        "white van delivery photo",
        "commercial van driving real image",
        "minivan city road photo",
        "cargo van parked roadside",
        "van driving in traffic",
        "real van on urban street",
        "delivery van highway photo",
        "van daylight outdoor image",
        "van natural street scene",
        "passenger minivan real photo",
        "realistic cargo van road",
        "van in city traffic",
        "transport van real image",
        "street van realistic photo",
    ],

    "ambulance": [
        "real ambulance on road",
        "ambulance driving real photo",
        "ambulance side view real image",
        "ambulance front view real photo",
        "ambulance rear view road photo",
        "emergency ambulance traffic image",
        "hospital ambulance real photo",
        "ambulance urban street scene",
        "ambulance highway real image",
        "paramedic ambulance road photo",
        "emergency medical vehicle real photo",
        "ambulance parked roadside",
        "ambulance in city traffic",
        "white ambulance real image",
        "ambulance daylight outdoor photo",
        "rescue ambulance street photo",
        "realistic ambulance driving",
        "ambulance natural lighting image",
        "ambulance emergency response vehicle",
        "ambulance realistic road scene",
    ],

    "police_car": [
        "real police car on street",
        "police cruiser driving real photo",
        "police car side view real image",
        "police car front view real photo",
        "police car rear view road photo",
        "patrol car traffic real image",
        "law enforcement vehicle real photo",
        "police vehicle urban street",
        "police car highway real image",
        "cop car road real photo",
        "police patrol vehicle street",
        "white police car real photo",
        "black police car road image",
        "police car parked roadside",
        "police car in traffic",
        "realistic police vehicle scene",
        "police sedan real road photo",
        "police SUV real photo",
        "police vehicle daylight image",
        "police car natural lighting",
    ],

    "fire_engine": [
        "real fire truck on road",
        "fire engine driving real photo",
        "fire truck side view real image",
        "fire truck front view real photo",
        "fire truck rear view road photo",
        "red fire truck real image",
        "fire department vehicle road photo",
        "emergency fire engine real photo",
        "firetruck urban street scene",
        "fire rescue truck real image",
        "fire truck traffic photo",
        "fire engine highway real photo",
        "fire truck parked roadside",
        "fire engine daylight outdoor image",
        "fire truck in city traffic",
        "ladder fire truck real photo",
        "rescue fire engine road image",
        "realistic fire truck street scene",
        "fire truck natural lighting photo",
        "emergency response fire vehicle",
    ],
}

# Thư mục lưu ảnh gốc: project_root/data/raw/<class>
PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR    = PROJECT_DIR / "data" / "raw"
BASE_DIR.mkdir(parents=True, exist_ok=True)
EDGE_PROFILE_DIR = PROJECT_DIR / ".edge_crawler_profile"
EDGE_FALLBACK_PROFILE_DIR = PROJECT_DIR / ".edge_crawler_profile_fallback"

# ── Mục tiêu ──────────────────────────────────────────────
IMAGES_PER_CLASS          = 5000
CRAWL_EXISTING_CLASSES_ONLY = False  # False = class đã có thì tải tiếp, class chưa có thì tạo mới và tải đủ
MAX_IMAGES_PER_KEYWORD    = 1500    # Mỗi keyword tải tối đa bao nhiêu rồi chuyển kw
DOWNLOAD_RETRIES          = 3
MAX_CONSECUTIVE_EMPTY_PAGES = 2

# ── API MODE params ────────────────────────────────────────
API_BASE_URL    = "https://api.magnific.com/v1/resources"
API_PAGE_LIMIT  = 100   # Số ảnh/request (max theo docs là 100)
API_MAX_PAGES   = 100   # page tối đa theo API docs (1-100)
API_WORKERS     = 12    # Luồng download song song
API_REQUEST_DELAY = 0.35  # Giữ dưới rate-limit trung bình, tránh khóa key/IP

# ── SELENIUM MODE params ───────────────────────────────────
SCROLL_WAIT        = 1.0
SCROLL_STEPS       = 10
SCROLL_PAUSE       = 0.35
DOWNLOAD_TIMEOUT   = 20
PAGE_LOAD_TIMEOUT  = 40
MAX_PAGES_PER_KW   = 25     # Web UI thực tế giới hạn ~20-25 trang
SELENIUM_WORKERS   = 12     # Luồng download song song
MAX_DRIVER_RESTARTS_PER_CLASS = 3

# ── Validate ảnh ──────────────────────────────────────────
MIN_IMAGE_BYTES  = 8_000
MIN_IMAGE_SIZE_PX = 100

VALID_CDN = (
    "img.freepik.com",
    "img.magnific.com",
    "preview.freepik.com",
    "ftcdn.net",
    "freepik.cdnpk.net",
)
BLOCKED_KEYWORDS = ("logo", "avatar", "icon", "sprite", "banner", "/ui/", "placeholder")

# ── Resume logic cho class đã tải dở ─────────────────────
CLASS_RESUME_KEYWORD_INDEX = {
    "car": [
        {"min_existing": 3400, "start_index": 5},
        {"min_existing": 1500, "start_index": 2},
    ],
}

# Thread lock để cập nhật counter an toàn
_counter_lock = threading.Lock()
_thread_local = threading.local()


class DriverSessionLost(RuntimeError):
    pass


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def md5_of_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def get_crawl_items() -> list[tuple[str, list[str]]]:
    """Trả về danh sách class cần crawl theo dữ liệu đang có."""
    if not CRAWL_EXISTING_CLASSES_ONLY:
        return list(VEHICLE_CLASSES.items())

    existing = {
        p.name for p in BASE_DIR.iterdir()
        if p.is_dir() and p.name in VEHICLE_CLASSES
    }
    if not existing:
        print("   [WARN] data/raw chưa có class nào, crawl toàn bộ class trong cấu hình.")
        return list(VEHICLE_CLASSES.items())

    skipped = [name for name in VEHICLE_CLASSES if name not in existing]
    if skipped:
        print("   [CONFIG] Chỉ crawl class đã có. Bỏ qua: " + ", ".join(skipped))
    return [(name, VEHICLE_CLASSES[name]) for name in VEHICLE_CLASSES if name in existing]


def is_valid_cdn_url(url: str) -> bool:
    if not url or url.startswith("data:image"):
        return False
    low = url.lower()
    host = urllib.parse.urlparse(low).hostname or ""
    if not any(host == cdn or host.endswith(f".{cdn}") for cdn in VALID_CDN):
        return False
    if any(kw in low for kw in BLOCKED_KEYWORDS):
        return False
    return True


def normalize_image_bytes(raw: bytes) -> bytes | None:
    """Validate PIL và trả về JPEG bytes đã chuẩn hóa để hash/lưu ổn định."""
    try:
        if len(raw) < MIN_IMAGE_BYTES:
            return None
        img = Image.open(BytesIO(raw)).convert("RGB")
        w, h = img.size
        if w < MIN_IMAGE_SIZE_PX or h < MIN_IMAGE_SIZE_PX:
            return None
        out = BytesIO()
        img.save(out, "JPEG", quality=90)
        return out.getvalue()
    except Exception:
        return None


def save_jpeg_bytes(data: bytes, save_path: Path) -> None:
    """Ghi file qua temp rồi replace để tránh file hỏng khi dừng đột ngột."""
    tmp_path = save_path.with_suffix(save_path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    tmp_path.replace(save_path)


def download_bytes(url: str, session: requests.Session) -> bytes | None:
    """Tải raw bytes, không lưu file."""
    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            resp = session.get(url, timeout=DOWNLOAD_TIMEOUT)
            if resp.status_code == 200:
                return resp.content
            if resp.status_code in (401, 403, 404):
                return None
            if resp.status_code == 429:
                time.sleep(2 * attempt)
            else:
                time.sleep(0.5 * attempt)
        except Exception:
            time.sleep(0.5 * attempt)
    return None


def get_worker_session(headers: dict, cookies: dict | None = None) -> requests.Session:
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        _thread_local.session = session
    session.headers.clear()
    session.headers.update(headers)
    session.cookies.clear()
    if cookies:
        session.cookies.update(cookies)
    return session


def load_seen_hashes(class_dir: Path) -> set[str]:
    hashes = set()
    for f in class_dir.glob("*.jpg"):
        try:
            hashes.add(md5_of_bytes(f.read_bytes()))
        except Exception:
            pass
    return hashes


def count_existing(class_dir: Path) -> int:
    return len(list(class_dir.glob("*.jpg")))


def get_next_file_index(class_dir: Path, class_name: str) -> int:
    max_index = -1
    prefix = f"{class_name}_"
    for fp in class_dir.glob(f"{class_name}_*.jpg"):
        stem = fp.stem
        if stem.startswith(prefix):
            suffix = stem[len(prefix):]
            if suffix.isdigit():
                max_index = max(max_index, int(suffix))
    return max_index + 1


def get_resume_keywords(class_name: str, keywords: list[str], downloaded: int) -> list[str]:
    rules = CLASS_RESUME_KEYWORD_INDEX.get(class_name)
    if not rules:
        return keywords
    rule = None
    for candidate in rules:
        if downloaded >= candidate["min_existing"]:
            rule = candidate
            break
    if rule is None:
        return keywords
    start_index = rule["start_index"]
    skipped = keywords[:start_index]
    resumed = keywords[start_index:]
    print("   [RESUME] Bỏ qua keyword đã crawl: " + ", ".join(f"'{k}'" for k in skipped))
    print("   [RESUME] Bắt đầu từ: " + (f"'{resumed[0]}'" if resumed else "không còn keyword"))
    return resumed


# ============================================================
# API MODE — Freepik/Magnific REST API
# ============================================================

def build_api_params(keyword: str, page: int, limit: int = API_PAGE_LIMIT) -> dict:
    """Tạo query params cho Freepik API /v1/resources."""
    return {
        "term":                         keyword,
        "page":                         page,
        "limit":                        limit,
        "order":                        "relevance",
        "filters[content_type][photo]": "true",
        "filters[ai_generated]":        "excluded",  # chỉ ảnh thật, không lấy AI-gen
    }


def fetch_api_page(keyword: str, page: int, session: requests.Session) -> tuple[list[str], int]:
    """
    Gọi Freepik API, trả về list URL ảnh từ kết quả.
    Xử lý rate-limit (429) bằng exponential back-off.
    """
    params = build_api_params(keyword, page)
    headers = {
        "x-magnific-api-key": MAGNIFIC_API_KEY,
        "Accept-Language":   "en-US",
        "Accept":            "application/json",
    }

    for attempt in range(1, 5):
        try:
            resp = session.get(API_BASE_URL, params=params, headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                urls = []
                for item in items:
                    img = item.get("image", {})
                    src = img.get("source", {})
                    url = src.get("url", "")
                    if url and is_valid_cdn_url(url):
                        # Loại bỏ query string nhưng giữ path
                        urls.append(url.split("?")[0])
                # Kiểm tra còn trang tiếp theo không
                meta = data.get("meta", {})
                last_page = meta.get("last_page", 1)
                return urls, last_page

            elif resp.status_code == 429:
                wait = 2 ** attempt
                print(f"   [API] Rate-limited, đợi {wait}s... (lần {attempt})")
                time.sleep(wait)
            else:
                print(f"   [API] HTTP {resp.status_code} khi lấy trang {page}, kw='{keyword}'")
                return [], 1

        except requests.RequestException as e:
            print(f"   [API] Lỗi kết nối: {e}")
            time.sleep(2)

    return [], 1


def _download_worker(args) -> tuple[str, bytes | None]:
    """Worker function cho ThreadPoolExecutor."""
    url, headers, cookies = args
    session = get_worker_session(headers, cookies)
    return url, download_bytes(url, session)


def crawl_class_api(class_name: str, keywords: list[str], target: int):
    """Crawl bằng Freepik API (không cần Selenium/đăng nhập)."""
    print(f"\n{'='*60}")
    print(f"🚀  [{class_name.upper()}]  — API MODE — mục tiêu {target} ảnh")
    print(f"{'='*60}")

    class_dir = BASE_DIR / class_name
    class_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes:   set[str] = load_seen_hashes(class_dir)
    seen_urls:     set[str] = set()
    downloaded     = count_existing(class_dir)
    next_file_index = get_next_file_index(class_dir, class_name)

    print(f"   [RESUME] Đã có: {downloaded} ảnh, {len(seen_hashes)} hash duy nhất.")
    if downloaded >= target:
        print("   ✅ Đã đủ. Bỏ qua.")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.magnific.com/",
    })

    active_keywords = get_resume_keywords(class_name, keywords, downloaded)
    if not active_keywords:
        print("   [WARN] Không còn keyword.")
        return

    for kw_idx, keyword in enumerate(active_keywords):
        if downloaded >= target:
            break

        kw_downloaded  = 0
        keyword_target = min(MAX_IMAGES_PER_KEYWORD, target - downloaded)
        empty_pages = 0
        print(
            f"\n▶️   Keyword {kw_idx+1}/{len(active_keywords)}: '{keyword}' "
            f"(mục tiêu keyword: {keyword_target})"
        )

        for page in range(1, API_MAX_PAGES + 1):
            if downloaded >= target or kw_downloaded >= keyword_target:
                break

            page_urls, last_page = fetch_api_page(keyword, page, session)
            new_urls = [u for u in page_urls if u not in seen_urls]
            seen_urls.update(new_urls)

            if not new_urls:
                empty_pages += 1
                print(f"   [API] Trang {page}: không còn ảnh mới ({empty_pages}/{MAX_CONSECUTIVE_EMPTY_PAGES}).")
                if empty_pages >= MAX_CONSECUTIVE_EMPTY_PAGES:
                    break
                continue
            empty_pages = 0

            # Download song song 10 luồng
            page_saved = 0
            remaining = min(target - downloaded, keyword_target - kw_downloaded)
            request_headers = dict(session.headers)
            pending = [(u, request_headers, None) for u in new_urls[:remaining]]

            with ThreadPoolExecutor(max_workers=API_WORKERS) as executor:
                futures = {executor.submit(_download_worker, arg): arg[0]
                           for arg in pending}
                for fut in as_completed(futures):
                    try:
                        url, raw = fut.result()
                    except Exception:
                        continue
                    if raw is None:
                        continue
                    normalized = normalize_image_bytes(raw)
                    if normalized is None:
                        continue
                    h = md5_of_bytes(normalized)
                    if h in seen_hashes:
                        continue
                    while (class_dir / f"{class_name}_{next_file_index:05d}.jpg").exists():
                        next_file_index += 1
                    save_path = class_dir / f"{class_name}_{next_file_index:05d}.jpg"
                    save_jpeg_bytes(normalized, save_path)
                    seen_hashes.add(h)
                    with _counter_lock:
                        downloaded       += 1
                        next_file_index  += 1
                        kw_downloaded    += 1
                        page_saved       += 1
                    if downloaded >= target or kw_downloaded >= keyword_target:
                        break

            print(
                f"   Trang {page:3d}/{last_page}: +{page_saved} mới | "
                f"kw={kw_downloaded} | tổng={downloaded}/{target}"
            )

            if page >= last_page:
                print(f"   [API] Đã tới trang cuối ({last_page}) của keyword này.")
                break

            # Nghỉ nhẹ giữa các request API
            time.sleep(API_REQUEST_DELAY)

        print(f"✅  Xong keyword '{keyword}': {kw_downloaded} ảnh mới.")

    print(f"\n🎉  HOÀN THÀNH [{class_name.upper()}]: {downloaded}/{target} ảnh.")


# ============================================================
# SELENIUM MODE — Web crawl bằng Edge (không cần API key)
# ============================================================

def create_driver_with_profile(profile_dir: Path):
    options = EdgeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.set_script_timeout(PAGE_LOAD_TIMEOUT)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def create_driver():
    for profile_dir in (EDGE_PROFILE_DIR, EDGE_FALLBACK_PROFILE_DIR):
        try:
            return create_driver_with_profile(profile_dir)
        except WebDriverException as exc:
            print(f"   [WARN] Không mở được Edge với profile {profile_dir.name}: {type(exc).__name__}")
            if profile_dir == EDGE_PROFILE_DIR:
                print("   [RECOVER] Thử profile dự phòng. Nếu profile chính đang mở, hãy đóng Edge trước lần chạy sau.")
                continue
            raise


def safe_get_cookies(driver) -> list[dict]:
    try:
        return driver.get_cookies()
    except Exception as exc:
        if "invalid session id" in str(exc).lower():
            raise DriverSessionLost("Session mất khi lấy cookie.") from exc
        return []


def safe_driver_get(driver, url: str, retries: int = 2) -> bool:
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            return True
        except InvalidSessionIdException as exc:
            raise DriverSessionLost("Session mất khi mở trang.") from exc
        except (TimeoutException, WebDriverException, Exception) as exc:
            if "invalid session id" in str(exc).lower():
                raise DriverSessionLost("Session mất khi mở trang.") from exc
            print(f"   [WARN] Mở trang lỗi ({attempt}/{retries}): {type(exc).__name__}")
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass
        time.sleep(2)
    return False


def build_search_url(keyword: str, page: int = 1) -> str:
    q = urllib.parse.quote_plus(keyword)
    return (
        f"https://www.magnific.com/search"
        f"?ai=excluded&format=search&query={q}&type=photo&page={page}"
    )


# JS để rút URL ảnh từ trang Magnific (chạy trong browser)
_JS_EXTRACT_URLS = """
const results = new Set();
const selectors = [
    'figure[data-cy="resource-thumbnail"] img',
    'figure img',
    'article img',
    '.photo-result img',
    '[data-type="photo"] img',
    'img'
];
let imgs = new Set();
for (const sel of selectors) {
    document.querySelectorAll(sel).forEach(img => imgs.add(img));
}
for (const img of imgs) {
    const attrs = [
        'currentSrc', 'src', 'data-src', 'data-lazy-src', 'data-original',
        'data-image-source', 'data-image', 'data-url'
    ];
    let found = false;
    for (const attr of attrs) {
        const val = attr === 'currentSrc' ? img.currentSrc : img.getAttribute(attr);
        if (val && !val.startsWith('data:image')) {
            results.add(val.split('?')[0]);
            found = true;
            break;
        }
    }
    if (!found) {
        const srcset = img.getAttribute('srcset') || img.getAttribute('data-srcset') || '';
        if (srcset) {
            const parts = srcset.split(',').map(s => s.trim().split(' ')[0]);
            if (parts.length) results.add(parts[parts.length-1].split('?')[0]);
        }
    }
}
document.querySelectorAll('source[srcset], source[data-srcset]').forEach(source => {
    const srcset = source.getAttribute('srcset') || source.getAttribute('data-srcset') || '';
    const parts = srcset.split(',').map(s => s.trim().split(' ')[0]).filter(Boolean);
    if (parts.length) results.add(parts[parts.length-1].split('?')[0]);
});
document.querySelectorAll('[style*="background"]').forEach(el => {
    const bg = window.getComputedStyle(el).backgroundImage || '';
    for (const match of bg.matchAll(/url\\(["']?([^"')]+)["']?\\)/g)) {
        if (match[1] && !match[1].startsWith('data:image')) results.add(match[1].split('?')[0]);
    }
});
return Array.from(results);
"""


def collect_page_urls(driver) -> list[str]:
    """Scroll dần và gom URL nhiều lần để bắt hết ảnh lazy-load."""
    collected: set[str] = set()
    last_count = 0
    stable_rounds = 0

    try:
        driver.execute_script("window.scrollTo(0, 0);")
    except Exception:
        pass
    time.sleep(0.3)

    for _ in range(SCROLL_STEPS):
        try:
            for url in driver.execute_script(_JS_EXTRACT_URLS) or []:
                collected.add(url)
        except Exception:
            pass

        try:
            driver.execute_script("window.scrollBy(0, Math.max(1200, window.innerHeight * 1.4));")
        except Exception:
            break
        time.sleep(SCROLL_PAUSE)

        if len(collected) == last_count:
            stable_rounds += 1
            if stable_rounds >= 3:
                break
        else:
            stable_rounds = 0
            last_count = len(collected)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)
        for url in driver.execute_script(_JS_EXTRACT_URLS) or []:
            collected.add(url)
    except Exception:
        pass

    return list(collected)


def crawl_class_selenium(driver, class_name: str, keywords: list[str], target: int):
    """Crawl bằng Selenium + download song song (không cần API key)."""
    print(f"\n{'='*60}")
    print(f"🚀  [{class_name.upper()}]  — SELENIUM MODE — mục tiêu {target} ảnh")
    print(f"{'='*60}")

    class_dir = BASE_DIR / class_name
    class_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes:   set[str] = load_seen_hashes(class_dir)
    seen_urls:     set[str] = set()
    downloaded     = count_existing(class_dir)
    next_file_index = get_next_file_index(class_dir, class_name)

    print(f"   [RESUME] Đã có: {downloaded} ảnh, {len(seen_hashes)} hash duy nhất.")
    if downloaded >= target:
        print("   ✅ Đã đủ. Bỏ qua.")
        return

    # Session request kế thừa cookie từ Selenium
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.magnific.com/",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    })

    active_keywords = get_resume_keywords(class_name, keywords, downloaded)
    if not active_keywords:
        print("   [WARN] Không còn keyword.")
        return

    for kw_idx, keyword in enumerate(active_keywords):
        if downloaded >= target:
            break

        kw_downloaded  = 0
        keyword_target = min(MAX_IMAGES_PER_KEYWORD, target - downloaded)
        empty_pages = 0
        print(
            f"\n▶️   Keyword {kw_idx+1}/{len(active_keywords)}: '{keyword}' "
            f"(mục tiêu keyword: {keyword_target})"
        )

        for page in range(1, MAX_PAGES_PER_KW + 1):
            if downloaded >= target or kw_downloaded >= keyword_target:
                break

            # Cập nhật cookie từ Selenium
            for cookie in safe_get_cookies(driver):
                session.cookies.set(cookie["name"], cookie["value"])

            url = build_search_url(keyword, page)
            if not safe_driver_get(driver, url):
                print(f"   [WARN] Trang {page}: bỏ qua, trình duyệt lỗi.")
                continue
            time.sleep(SCROLL_WAIT)

            # Đóng overlay cookie nếu xuất hiện
            try:
                accept = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                accept.click()
                time.sleep(0.5)
            except Exception:
                pass

            raw_urls = collect_page_urls(driver)
            valid_urls_all = [u for u in raw_urls if is_valid_cdn_url(u)]
            valid_urls = [u for u in valid_urls_all if u not in seen_urls]
            seen_urls.update(valid_urls)

            if not valid_urls:
                empty_pages += 1
                print(
                    f"   [WARN] Trang {page}: raw={len(raw_urls)} | valid={len(valid_urls_all)} | "
                    f"new=0 ({empty_pages}/{MAX_CONSECUTIVE_EMPTY_PAGES})."
                )
                if empty_pages >= MAX_CONSECUTIVE_EMPTY_PAGES:
                    break
                continue
            empty_pages = 0

            # Download song song SELENIUM_WORKERS luồng
            page_saved = 0
            pending_urls = []
            remaining = min(target - downloaded, keyword_target - kw_downloaded)
            for u in valid_urls:
                if len(pending_urls) >= remaining:
                    break
                pending_urls.append(u)

            request_headers = dict(session.headers)
            request_cookies = session.cookies.get_dict()
            failed_download = 0
            invalid_image = 0
            duplicate_hash = 0
            with ThreadPoolExecutor(max_workers=SELENIUM_WORKERS) as executor:
                futures = {executor.submit(_download_worker, (u, request_headers, request_cookies)): u
                           for u in pending_urls}
                for fut in as_completed(futures):
                    try:
                        url_dl, raw = fut.result()
                    except Exception:
                        failed_download += 1
                        continue
                    if raw is None:
                        failed_download += 1
                        continue
                    normalized = normalize_image_bytes(raw)
                    if normalized is None:
                        invalid_image += 1
                        continue
                    h = md5_of_bytes(normalized)
                    if h in seen_hashes:
                        duplicate_hash += 1
                        continue
                    while (class_dir / f"{class_name}_{next_file_index:05d}.jpg").exists():
                        next_file_index += 1
                    save_path = class_dir / f"{class_name}_{next_file_index:05d}.jpg"
                    save_jpeg_bytes(normalized, save_path)
                    seen_hashes.add(h)
                    with _counter_lock:
                        downloaded       += 1
                        next_file_index  += 1
                        kw_downloaded    += 1
                        page_saved       += 1
                    if downloaded >= target or kw_downloaded >= keyword_target:
                        break

            print(
                f"   Trang {page:3d}: raw={len(raw_urls)} | valid={len(valid_urls_all)} | "
                f"new={len(valid_urls)} | +{page_saved} lưu | "
                f"fail={failed_download} invalid={invalid_image} dup={duplicate_hash} | "
                f"kw={kw_downloaded} | tổng={downloaded}/{target}"
            )

            if len(valid_urls) < 5:
                print(f"   [INFO] Trang {page} ít ảnh ({len(valid_urls)}), chuyển keyword.")
                break

            time.sleep(0.8)   # Giảm từ 1.0 → 0.8s

        print(f"✅  Xong keyword '{keyword}': {kw_downloaded} ảnh mới.")

    print(f"\n🎉  HOÀN THÀNH [{class_name.upper()}]: {downloaded}/{target} ảnh.")


# ============================================================
# MAIN
# ============================================================

def main():
    if USE_API_MODE:
        # ── API MODE ───────────────────────────────────────
        print("\n" + "="*60)
        print("🔑  CHẾ ĐỘ: API MODE (Freepik/Magnific REST API)")
        print("    Không cần đăng nhập / trình duyệt.")
        print("    ⚠️  Lưu ý: Đọc ToS tại magnific.com/api trước khi dùng.")
        print("="*60 + "\n")

        for class_name, keywords in get_crawl_items():
            try:
                crawl_class_api(class_name, keywords, IMAGES_PER_CLASS)
            except KeyboardInterrupt:
                print("\n⚠️  Người dùng dừng (Ctrl+C).")
                break
            except Exception as exc:
                print(f"\n[ERROR] Lớp {class_name} lỗi: {exc}")

    else:
        # ── SELENIUM MODE ──────────────────────────────────
        print("\n" + "="*60)
        print("🌐  CHẾ ĐỘ: SELENIUM MODE (Edge browser)")
        print("    Tip: Đặt MAGNIFIC_API_KEY để dùng API mode nhanh hơn.")
        print("="*60 + "\n")

        driver = create_driver()
        safe_driver_get(driver, "https://www.magnific.com/", retries=3)
        print("\n" + "!"*60)
        print("🛑  TRÌNH DUYỆT ĐÃ MỞ!")
        print("👉  Hãy ĐĂNG NHẬP vào tài khoản Magnific (hoặc Google).")
        print("    Sau khi vào trang chủ thì quay lại đây.")
        input("✅  ĐĂNG NHẬP XONG → Nhấn [ENTER] để bắt đầu crawl: ")
        print("!"*60 + "\n")

        class_items    = get_crawl_items()
        class_index    = 0
        restart_count  = 0

        try:
            while class_index < len(class_items):
                class_name, keywords = class_items[class_index]
                try:
                    crawl_class_selenium(driver, class_name, keywords, IMAGES_PER_CLASS)
                    class_index   += 1
                    restart_count  = 0
                except DriverSessionLost as exc:
                    restart_count += 1
                    print(f"\n[WARN] Browser session mất: {exc}")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    if restart_count > MAX_DRIVER_RESTARTS_PER_CLASS:
                        print(f"[ERROR] {class_name} mất session quá {MAX_DRIVER_RESTARTS_PER_CLASS} lần → chuyển class.")
                        class_index  += 1
                        restart_count = 0
                    print("[RECOVER] Đang mở lại Edge...")
                    driver = create_driver()
                    safe_driver_get(driver, "https://www.magnific.com/", retries=3)
                    time.sleep(3)
                except Exception as exc:
                    print(f"\n[ERROR] Lớp {class_name} lỗi, chuyển tiếp: {exc}")
                    class_index += 1
                    restart_count = 0
        except KeyboardInterrupt:
            print("\n⚠️  Người dùng dừng (Ctrl+C). Đóng trình duyệt...")
        finally:
            driver.quit()
            print("\n🏁  ĐÃ ĐÓNG TRÌNH DUYỆT. XONG.")


if __name__ == "__main__":
    main()
