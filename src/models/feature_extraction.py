# Đường dẫn: src/models/feature_extraction.py

import cv2
import numpy as np
import math
from skimage import feature

# Import tương thích ngược cho các phiên bản scikit-image khác nhau
try:
    from skimage.feature import hog, graycomatrix, graycoprops
except ImportError:
    from skimage.feature import hog, greycomatrix as graycomatrix, greycoprops as graycoprops

# Import hàm resize từ file utils
from src.models.utils.preprocessing import resize_with_padding

def extract_hsv_histogram(image_norm):
    """Trích xuất màu sắc bằng HSV Histogram (Đã tối ưu hóa xuống 64 bins)"""
    # Đưa ảnh về uint8 [0, 255]
    image_uint8 = (image_norm * 255).astype(np.uint8)
    
    # Chuyển đổi sang HSV
    hsv = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2HSV)
    
    # Giảm từ 8x8x8=512 xuống 4x4x4=64 bins để cân bằng trọng số các đặc trưng khác
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [4, 4, 4], [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten() # 64 chiều

def extract_lbp(image_norm, num_points=24, radius=3):
    """Trích xuất kết cấu bằng Local Binary Pattern (LBP)"""
    image_uint8 = (image_norm * 255).astype(np.uint8)
    gray = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2GRAY)
    
    lbp = feature.local_binary_pattern(gray, num_points, radius, method="uniform")
    
    n_bins = num_points + 2
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
    return hist # 26 chiều

def extract_hu_moments(image_norm):
    """Trích xuất hình dạng bằng Hu Moments (Sử dụng ngưỡng tự động Otsu)"""
    image_uint8 = (image_norm * 255).astype(np.uint8)
    gray = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2GRAY)
    
    # Dùng Otsu's thresholding để tự động nhị phân hóa thay vì ngưỡng tĩnh 128
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    moments = cv2.moments(thresh)
    hu = cv2.HuMoments(moments)
    
    hu_log = []
    for h in hu:
        h_val = h[0]
        if h_val != 0:
            hu_log.append(-1 * math.copysign(1.0, h_val) * math.log10(abs(h_val)))
        else:
            hu_log.append(0.0)
    return np.array(hu_log) # 7 chiều

def extract_glcm_features(image_norm):
    """Trích xuất đặc trưng kết cấu GLCM (Haralick)"""
    image_uint8 = (image_norm * 255).astype(np.uint8)
    gray = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2GRAY)
    
    # Chia nhỏ thành 16 mức xám để tính toán GLCM nhanh chóng và tránh thưa thớt (sparse)
    gray_16 = (gray / 16).astype(np.uint8)
    
    # Tính ma trận GLCM cho 2 khoảng cách (1, 2 px) và 4 hướng xoay
    glcm = graycomatrix(gray_16, distances=[1, 2], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                        levels=16, symmetric=True, normed=True)
    
    # Trích xuất 5 tính chất thống kê
    props = ['contrast', 'correlation', 'energy', 'homogeneity', 'dissimilarity']
    glcm_feats = []
    for prop in props:
        glcm_feats.extend(graycoprops(glcm, prop).flatten())
        
    return np.array(glcm_feats) # 2 khoảng cách * 4 hướng * 5 tính chất = 40 chiều

def extract_hog_features(image_norm):
    """Trích xuất đặc trưng cấu trúc HOG (Histogram of Oriented Gradients)"""
    image_uint8 = (image_norm * 255).astype(np.uint8)
    gray = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2GRAY)
    
    # Trích xuất HOG với cell 16x16 cho ảnh 224x224
    hog_feats = hog(gray, orientations=9, pixels_per_cell=(16, 16), 
                   cells_per_block=(2, 2), visualize=False, channel_axis=None)
    
    return hog_feats # 6084 chiều

def extract_all_features(image_path):
    """Hàm Pipeline kết hợp tất cả đặc trưng truyền thống: Màu sắc, Kết cấu, Hình dạng và Cấu trúc"""
    # 1. Tiền xử lý (Resize & Padding)
    img_norm = resize_with_padding(image_path)
    
    # 2. Rút trích các nhóm đặc trưng
    f_color = extract_hsv_histogram(img_norm)        # 64 chiều
    f_lbp = extract_lbp(img_norm)                    # 26 chiều
    f_hu = extract_hu_moments(img_norm)              # 7 chiều
    f_glcm = extract_glcm_features(img_norm)         # 40 chiều
    f_hog = extract_hog_features(img_norm)           # 6084 chiều
    
    # 3. Nối các nhóm mảng lại thành một Vector tổng hợp (Tổng: 6221 chiều)
    return np.concatenate((f_color, f_lbp, f_hu, f_glcm, f_hog), axis=0)