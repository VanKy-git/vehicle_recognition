# Hệ thống Phân loại Rau Củ Quả

## Mục tiêu
- Train CNN bằng PyTorch.
- Train Random Forest bằng scikit-learn trên đặc trưng trích xuất.
- Demo dự đoán qua Flask.

## Cấu trúc chính
- `data/raw/`: dữ liệu gốc sau crawl.
- `data/processed/`: dữ liệu đã xử lý và chia train/val/test.
- `src/models/`: mã train và trích xuất đặc trưng.
- `weights/models/`: model đã train xong.
- `app/web/`: web demo Flask.
- `docs/`: báo cáo, metrics, confusion matrix.

## Setup nhanh
1. Tạo môi trường ảo cục bộ.
2. Cài dependencies từ `requirements.txt`.
3. Điền biến môi trường trong `.env`.
4. Chạy script train hoặc Flask demo.
