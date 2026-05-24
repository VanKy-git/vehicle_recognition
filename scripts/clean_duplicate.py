import os
import hashlib
from pathlib import Path

# Dẫn hướng thư mục giống hệt file download_data.py
SCRIPT_DIR = Path(__file__).parent.parent 
BASE_DIR = str(SCRIPT_DIR / "data" / "raw")

def get_md5_hash(file_path):
    """Doc file nhi phan va bam ra ma MD5"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # Doc theo chunk de khong bi tran RAM neu anh qua nang
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicates(base_folder):
    print("--------------------------------------------------")
    print("[SYSTEM] BAT DAU TIEN TRINH LOC ANH TRUNG LAP (MD5)")
    print("--------------------------------------------------")
    
    if not os.path.exists(base_folder):
        print(f"[ERROR] Khong tim thay thu muc du lieu: {base_folder}")
        return

    total_scanned = 0
    total_removed = 0
    
    # Duyet qua cac thu muc con (car, bus, truck...)
    for class_name in sorted(os.listdir(base_folder)):
        class_dir = os.path.join(base_folder, class_name)
        
        if not os.path.isdir(class_dir):
            continue
            
        print(f"\n[PROCESSING] Dang xu ly thu muc: {class_name.upper()}")
        
        hashes = set()
        class_initial_count = 0
        class_removed_count = 0
        
        # Quet toan bo file trong thu muc class
        for filename in os.listdir(class_dir):
            file_path = os.path.join(class_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
                
            class_initial_count += 1
            total_scanned += 1
            
            file_hash = get_md5_hash(file_path)
            
            # Phat hien trung lap
            if file_hash in hashes:
                os.remove(file_path)
                class_removed_count += 1
                total_removed += 1
            else:
                hashes.add(file_hash)
                
        class_remaining = class_initial_count - class_removed_count
        
        # In log kieu terminal truyen thong
        print(f"    - So anh ban dau    : {class_initial_count}")
        print(f"    - So anh bi xoa     : {class_removed_count}")
        print(f"    - So anh con lai    : {class_remaining}")
        
    print("\n--------------------------------------------------")
    print("[COMPLETED] TONG KET QUA TRINH LOC")
    print("--------------------------------------------------")
    print(f"Tong so anh tai ve thanh cong : {total_scanned}")
    print(f"Tong so anh trung lap bi xoa  : {total_removed}")
    print(f"Tong so anh sach con lai      : {total_scanned - total_removed}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    remove_duplicates(BASE_DIR)