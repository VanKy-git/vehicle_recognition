import os
import numpy as np
from src.models.feature_extraction import extract_all_features

def load_data(data_dir="data/raw"):
    """
    Duyệt qua thư mục data_dir, trích xuất đặc trưng của từng ảnh
    và trả về tập dữ liệu X (features) và y (labels) để huấn luyện Random Forest.
    """
    X = []
    y = []
    
    if not os.path.exists(data_dir):
        print(f"⚠️ Cảnh báo: Thư mục '{data_dir}' chưa tồn tại. Vui lòng tạo thư mục và thêm ảnh.")
        return np.array(X), np.array(y)
    
    # Lấy danh sách các thư mục con (mỗi thư mục đại diện cho 1 lớp phương tiện)
    classes = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    print(f"Tìm thấy {len(classes)} lớp phương tiện: {classes}")
    
    for label_idx, class_name in enumerate(classes):
        class_path = os.path.join(data_dir, class_name)
        # Quét tất cả các file ảnh trong thư mục lớp
        for file_name in os.listdir(class_path):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                img_path = os.path.join(class_path, file_name)
                try:
                    # Trích xuất đặc trưng
                    features = extract_all_features(img_path)
                    X.append(features)
                    y.append(label_idx)
                except Exception as e:
                    print(f"❌ Lỗi xử lý ảnh {img_path}: {e}")
                    
    return np.array(X), np.array(y)
