import os
import shutil
import random
import cv2
import numpy as np
from src.models.utils.preprocessing import resize_with_padding

def split_and_preprocess_dataset(raw_dir="data/raw", processed_dir="data/processed", train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_seed=42):
    """
    Phân chia dữ liệu từ thư mục raw thành 3 tập train, val, test với tỷ lệ chỉ định (70/15/15),
    đồng thời áp dụng tiền xử lý (resize & padding) và lưu vào thư mục processed.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-9, "Tổng tỷ lệ train, val, test phải bằng 1.0"
    
    random.seed(random_seed)
    
    if not os.path.exists(raw_dir):
        print(f"❌ Thư mục dữ liệu gốc '{raw_dir}' không tồn tại.")
        return
        
    classes = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    print(f"📂 Tìm thấy {len(classes)} lớp phương tiện: {classes}")
    
    # Tạo cấu trúc thư mục processed/train, processed/val, processed/test
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(processed_dir, split), exist_ok=True)
        for class_name in classes:
            os.makedirs(os.path.join(processed_dir, split, class_name), exist_ok=True)

    for class_name in classes:
        class_path = os.path.join(raw_dir, class_name)
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        # Xáo trộn danh sách ảnh ngẫu nhiên để đảm bảo tính khách quan
        random.shuffle(images)
        
        n_images = len(images)
        n_train = int(n_images * train_ratio)
        n_val = int(n_images * val_ratio)
        
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]
        
        print(f"\n📊 Lớp '{class_name}': Tổng cộng {n_images} ảnh.")
        print(f"   - Train (70%): {len(train_images)} ảnh")
        print(f"   - Val (15%): {len(val_images)} ảnh")
        print(f"   - Test (15%): {len(test_images)} ảnh")
        
        splits = {
            'train': train_images,
            'val': val_images,
            'test': test_images
        }
        
        for split_name, split_files in splits.items():
            for filename in split_files:
                src_path = os.path.join(class_path, filename)
                dest_path = os.path.join(processed_dir, split_name, class_name, filename)
                
                try:
                    # 1. Gọi hàm tiền xử lý (trả về ảnh normalized float32)
                    img_norm = resize_with_padding(src_path)
                    
                    # 2. Chuyển đổi ngược về uint8 (0-255) để lưu thành file ảnh
                    img_uint8 = (img_norm * 255).astype(np.uint8)
                    
                    # 3. Lưu ảnh đã tiền xử lý vào thư mục tương ứng trong processed/
                    cv2.imwrite(dest_path, img_uint8)
                except Exception as e:
                    print(f"   ❌ Lỗi khi tiền xử lý/sao chép {filename}: {e}")

    print("\n✅ Hoàn thành việc phân chia và tiền xử lý dữ liệu vật lý!")

if __name__ == "__main__":
    # Điểm chạy trực tiếp để kiểm tra hoặc chia dữ liệu nhanh
    split_and_preprocess_dataset(
        raw_dir="data/raw",
        processed_dir="data/processed",
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
