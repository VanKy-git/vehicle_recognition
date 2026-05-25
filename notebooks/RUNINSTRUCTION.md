# HƯỚNG DẪN TIỀN XỬ LÝ & TRÍCH XUẤT ĐẶC TRƯNG PHƯƠNG TIỆN

Tài liệu này hướng dẫn chi tiết các bước để chuẩn bị dữ liệu, chạy trích xuất đặc trưng và trực quan hóa phân cụm cho mô hình phân loại phương tiện.

---

## 📂 Sơ đồ Luồng Dữ liệu (Data Pipeline)

1. **Ảnh Thô** (`data/raw/`) $\rightarrow$ 
2. **Chia & Tiền xử lý** (`data/processed/`) $\rightarrow$ 
3. **Trích xuất Đặc trưng** (`data/features/`) $\rightarrow$ 
4. **Trực quan hóa** (`notebooks/feature_visualization.ipynb`)

---

## 🛠️ Các Bước Thực Hiện Chi Tiết

> [!IMPORTANT]
> Hãy chắc chắn rằng bạn đang sử dụng môi trường **Python 3.11.9**  vì môi trường này đã được cài đặt đầy đủ các thư viện xử lý ảnh.

### Bước 1: Phân chia & Tiền xử lý Dữ liệu Vật lý
Bước này sẽ chia dữ liệu gốc (10 lớp, mỗi lớp 1000 ảnh) theo tỷ lệ **70/15/15** (Train/Val/Test), tự động resize ảnh về kích thước **224x224 kèm theo padding đen** chống méo hình và chuẩn hóa pixel về đoạn $[0.0, 1.0]$.

Mở terminal Git Bash tại thư mục gốc dự án (`vehicle_recognition`) và chạy lệnh:
```bash
python -m src.models.utils.split_dataset
```
* **Kết quả:** Ảnh sạch sẽ được lưu tương ứng vào `data/processed/train/`, `data/processed/val/`, và `data/processed/test/`.

---

### Bước 2: Chạy Trích xuất Đặc trưng truyền thống
Bước này sẽ duyệt qua toàn bộ ảnh sạch đã tiền xử lý ở Bước 1, trích xuất tổ hợp đặc trưng phong phú **6221 chiều** và đóng gói thành file NumPy `.npy` cho mô hình Random Forest.
* Đặc trưng màu sắc: **HSV Histogram** (64 chiều).
* Đặc trưng kết cấu cục bộ: **LBP Histogram** (26 chiều).
* Đặc trưng hình khối bất biến: **Hu Moments** (7 chiều).
* Đặc trưng phân bố kết cấu không gian: **Haralick GLCM** (40 chiều).
* Đặc trưng viền cấu trúc vật thể: **HOG** (6084 chiều).

Chạy lệnh dưới đây từ terminal:
```bash
python scripts/prepare_features.py
```
* **Kết quả:** Các file đặc trưng được đóng gói nhanh chóng tại thư mục `data/features/`:
  * `X_train.npy` (7000, 6221) & `y_train.npy` (7000,)
  * `X_val.npy` (1500, 6221) & `y_val.npy` (1500,)
  * `X_test.npy` (1500, 6221) & `y_test.npy` (1500,)

---

### Bước 3: Chạy Trực quan hóa Đặc trưng & Báo cáo
Sử dụng file Jupyter Notebook `notebooks/feature_visualization.ipynb` để trực quan hóa toàn bộ tiến trình báo cáo.

1. Mở file `notebooks/feature_visualization.ipynb` trong VS Code.
2. Tại góc trên cùng bên phải màn hình, chọn Kernel là **`Python 3.11.9`** (Môi trường hệ thống chứa OpenCV, Matplotlib...).
3. Chạy cell đầu tiên (`%pip install -r ../requirements.txt`) nếu môi trường của bạn chưa cài đặt thư viện. Nếu đã có sẵn thư viện, bạn có thể bỏ qua cell này.
4. Chạy các cell tiếp theo để:
   * Xem ảnh so sánh trực quan Trước/Sau khi tiền xử lý (Nhiệm vụ 1).
   * Trực quan hóa các kênh màu HSV, bản đồ LBP Texture Map, ma trận Haralick GLCM Heatmap, ảnh nhị phân phân tách nền Otsu và đặc trưng viền HOG Map (Nhiệm vụ 2).
   * Vẽ biểu đồ phân cụm **PCA** và **t-SNE** sau khi dữ liệu đã đi qua bộ chuẩn hóa **StandardScaler** (Nhiệm vụ 3).

---

## ⚠️ Lưu ý khi làm việc nhóm trên Git
Các thư mục dữ liệu ảnh nặng và đặc trưng đóng gói không được đẩy lên GitHub để tránh làm nặng repository. File `.gitignore` ở thư mục gốc đã được thiết lập để tự động bỏ qua các thư mục này:
```text
/data/      # Bỏ qua toàn bộ ảnh thô, ảnh sạch và đặc trưng
*.npy       # Bỏ qua các file mảng numpy đặc trưng
```
