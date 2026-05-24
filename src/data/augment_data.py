import os
from PIL import Image
from torchvision import transforms

# Lưu ý: Kiểm tra kỹ tên thư mục: processed (2 chữ s) hay processsed (3 chữ s)
INPUT_DIR = 'data/processed/train' 
OUTPUT_DIR = 'data/augmented_train'

augment_machine = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5), # Nên để 0.5 để đa dạng, không phải ảnh nào cũng lật
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.GaussianBlur(kernel_size=3)
])

for class_name in os.listdir(INPUT_DIR):
    class_path_in = os.path.join(INPUT_DIR, class_name)
    class_path_out = os.path.join(OUTPUT_DIR, class_name)
    
    if not os.path.isdir(class_path_in): continue # Bỏ qua nếu không phải thư mục
    
    os.makedirs(class_path_out, exist_ok=True)
    
    print(f"--- Đang xử lý lớp: {class_name} ---")
    
    for filename in os.listdir(class_path_in):
        # Chỉ xử lý ảnh jpg/jpeg/png
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                img_path = os.path.join(class_path_in, filename)
                
                # Mở và chuyển sang RGB (để tránh lỗi ảnh RGBA 4 kênh khi lưu JPEG)
                original_img = Image.open(img_path).convert("RGB")
                
                augmented_img = augment_machine(original_img)
                
                new_filename = filename.rsplit(".", 1)[0] + "_aug.jpg"
                save_path = os.path.join(class_path_out, new_filename)
                
                augmented_img.save(save_path, "JPEG", quality=90)
            except Exception as e:
                print(f"Lỗi ở file {filename}: {e}")
                continue # Bỏ qua file lỗi, chạy tiếp file sau
            
    print(f"Xong lớp: {class_name}")