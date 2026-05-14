🚀 HƯỚNG DẪN SỬ DỤNG CẤU TRÚC FOLDER DỰ ÁN
Đề tài: Hệ thống Phân loại Rau Củ Quả (Team 4 người)

Chào anh em! Để dự án không bị nát, GitHub không bị treo và code không đè lên nhau, anh em VUI LÒNG đọc kỹ bản đồ này trước khi nhét file vào folder nhé. Nguyên tắc tối thượng: "Đồ của ai, việc của người nấy, bỏ đúng chỗ!"

🗺️ BẢN ĐỒ FOLDER CHO TỪNG NGƯỜI
👨‍💻 1. NHUẬN (Team Data & Crawl)
📂 scripts/: Nơi Nhuận bỏ các file code chạy 1 lần.

Ví dụ: download_data.py (Selenium), clean_duplicate.py (băm MD5).

📂 data/: Nơi chứa toàn bộ ảnh tải về.

Bỏ ảnh gốc mới crawl vào data/raw/.

Lưu ý: Folder này đã bị khóa lại, Nhuận cứ thoải mái tải 10GB ảnh về máy mà không sợ bị đẩy nhầm lên GitHub làm nặng máy anh em.

📂 notebooks/: Nhuận code file EDA_thống_kê.ipynb ở đây để vẽ biểu đồ tròn, cột nhé.

👨‍💻 2. NHẬT (Team Xử lý ảnh & Đặc trưng)
📂 src/: Nơi chứa code nền tảng. Nhật tạo các file như preprocess.py (Resize 224x224), feature_extraction.py (Lấy màu HSV, LBP, Haralick) ở trong này.

📂 data/processed/: Sau khi cắt gọt chuẩn hóa xong, Nhật lưu bộ ảnh sạch sẽ nhất vào đây để Kỳ và Quốc bốc ra train model.

👨‍💻 3. KỲ & QUỐC (Team Build Model)
📂 src/models/:

Kỳ: Bỏ file code train_cnn.py vào đây.

Quốc: Bỏ file code train_rf.py vào đây.

📂 weights/models/: Nơi xuất ra thành phẩm. Khi model train xong, anh em nhớ code lệnh lưu file đuôi .pth (Kỳ) hoặc .pkl (Quốc) vào đúng folder này.

Lưu ý: Folder này cũng đã bị khóa không cho up lên Git.

📂 docs/metrics/: Chạy xong nhớ lưu ảnh chụp đồ thị Loss/Accuracy, ma trận nhầm lẫn vào đây để làm báo cáo.

👨‍💻 4. PHẦN CHẠY WEB DEMO (Ai phụ trách web thì xem)
📂 app/: Toàn bộ sinh mệnh của Website nằm riêng ở đây. Đừng vứt lộn ra ngoài.

app.py: Code server.

templates/: Giao diện HTML.

static/: Chứa CSS, JS và ảnh người dùng upload.

🛑 QUY TẮC SINH TỒN (BẮT BUỘC NHỚ)
Tuyệt đối KHÔNG push file nặng lên Git: Bất kỳ file nào là ảnh (.jpg, .png), tệp dữ liệu (.csv to), tệp mô hình nặng (.pth, .pkl) đều ĐÃ BỊ CHẶN bởi file .gitignore. Nếu Git báo lỗi dung lượng, kiểm tra ngay xem có lỡ vứt file nặng ra sai thư mục không!

Không up môi trường ảo: Ai cài thư viện gì thì máy người đó tự chịu. KHÔNG đưa thư mục venv hoặc .env lên GitHub.

Cập nhật thư viện: Nếu anh em cài thêm thư viện mới (ví dụ pip install seaborn), nhớ gõ lệnh pip freeze > requirements.txt rồi push file text đó lên để anh em khác biết đường cài theo.