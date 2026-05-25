# Đường dẫn: src/utils/image_preprocessing.py

import cv2
import numpy as np
import os

def resize_with_padding(image_path, target_size=(224, 224)):
    """
    Hàm đọc ảnh từ thư mục, thu phóng giữ nguyên tỷ lệ và thêm viền đen (padding).
    
    Cú pháp/Tham số:
    - image_path (str): Đường dẫn tuyệt đối hoặc tương đối tới file ảnh. 
                        Ví dụ: "../../data/raw/xe_may/image_001.jpg"
    - target_size (tuple): Kích thước mục tiêu (Rộng, Cao).
    """
    # 1. Kiểm tra xem file có tồn tại không
    if not os.path.exists(image_path):
        raise ValueError(f"Không tìm thấy ảnh tại đường dẫn: {image_path}")
        
    # 2. Đọc ảnh bằng OpenCV (cv2.imread trả về ma trận pixel BGR)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Lỗi đọc ảnh (file hỏng hoặc không đúng định dạng): {image_path}")

    # 3. Tính toán tỷ lệ thu phóng sao cho không làm méo ảnh
    h, w = img.shape[:2]
    scale = min(target_size[0]/w, target_size[1]/h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    # Phương thức cv2.resize: thu nhỏ/phóng to ma trận ảnh
    # cv2.INTER_AREA: thuật toán nội suy tốt nhất khi thu nhỏ ảnh
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # 4. Tạo một khung canvas đen hoàn toàn (tất cả pixel = 0)
    # np.zeros tạo ma trận với kiểu dữ liệu uint8 (0-255)
    canvas = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
    
    # 5. Dán ảnh đã resize vào chính giữa canvas
    x_offset = (target_size[0] - new_w) // 2
    y_offset = (target_size[1] - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    # 6. Normalize (Chuẩn hóa pixel từ 0-255 về 0.0-1.0)
    normalized_img = canvas.astype('float32') / 255.0
    
    return normalized_img