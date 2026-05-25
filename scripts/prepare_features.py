import os
import sys
import numpy as np

# Thêm thư mục gốc vào PYTHONPATH để nhận diện package src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.utils.data_loader import load_data

def main():
    processed_dir = "data/processed"
    features_dir = "data/features"
    
    if not os.path.exists(processed_dir):
        print(f" Không tìm thấy thư mục dữ liệu đã tiền xử lý '{processed_dir}'. Vui lòng chạy split_dataset.py trước.")
        return
        
    os.makedirs(features_dir, exist_ok=True)
    splits = ["train", "val", "test"]
    
    for split in splits:
        split_path = os.path.join(processed_dir, split)
        print(f"\n Đang trích xuất đặc trưng cho tập {split.upper()}...")
        
        # Load và trích xuất
        X, y = load_data(split_path)
        
        if len(X) == 0:
            print(f" Tập {split.upper()} không có dữ liệu để trích xuất.")
            continue
            
        # Đường dẫn lưu file
        X_save_path = os.path.join(features_dir, f"X_{split}.npy")
        y_save_path = os.path.join(features_dir, f"y_{split}.npy")
        
        # Lưu vào disk dưới định dạng numpy array (.npy)
        np.save(X_save_path, X)
        np.save(y_save_path, y)
        
        print(f" Đã lưu tập {split.upper()}:")
        print(f"   - X_{split} (kích thước: {X.shape}) -> '{X_save_path}'")
        print(f"   - y_{split} (kích thước: {y.shape}) -> '{y_save_path}'")
        
    print("\n Hoàn thành trích xuất toàn bộ đặc trưng! Sẵn sàng cho việc train Random Forest.")

if __name__ == "__main__":
    main()
