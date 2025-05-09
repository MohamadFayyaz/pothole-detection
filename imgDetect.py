from ultralytics import YOLO
import cv2

# Muat model YOLOv8 (ganti 'path/ke/model_anda.pt' dengan path model Anda)
model = YOLO('best.pt')

# Lakukan deteksi pada gambar (ganti 'path/ke/gambar_anda.jpg' dengan path gambar Anda)
results = model('dataset/jalan.jpg')
# img = cv2.resize(img, (1020, 500))

# Tampilkan hasil deteksi
for r in results:
    im_array = r.plot()  # Menggambar kotak pembatas dan label pada gambar
    resized_result = cv2.resize(im_array, (800, 600))
    cv2.imshow('Hasil Deteksi YOLOv8', resized_result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()