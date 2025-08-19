import cv2
import easyocr
import torch
import os
import pymysql
from datetime import datetime

# Load YOLO model once
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'])

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,  # use 33060 only if MySQL X Protocol is enabled
    'user': 'root',
    'password': 'Bo92mloboa$',
    'database': 'car_park_db'
}

def save_plate_to_db(plate_text):
    """Insert detected plate into MySQL using PyMySQL."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO number_plates (plate_number, detected_at) VALUES (%s, %s)"  # <-- fixed column name
        cursor.execute(query, (plate_text, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[+] Saved plate '{plate_text}' to database.")
    except pymysql.MySQLError as err:
        print(f"[!] Database error: {err}")

def get_number_plate():
    """Detects and reads a number plate from test_plate.jpeg."""
    base_dir = os.path.dirname(__file__)
    img_path = os.path.abspath(os.path.join(base_dir, '..', 'test_plate.jpeg'))

    img = cv2.imread(img_path)
    if img is None:
        print("[-] Could not load image.")
        return None

    results = model(img)
    os.makedirs("plate_outputs", exist_ok=True)

    for i, (*box, conf, cls) in enumerate(results.xyxy[0]):
        x1, y1, x2, y2 = map(int, box)
        cropped = img[y1:y2, x1:x2]
        cv2.imwrite(f"plate_outputs/plate_{i}.jpeg", cropped)

        ocr_result = reader.readtext(cropped)
        if ocr_result:
            plate_text = ocr_result[0][-2]
            print(f"[+] Detected Plate #{i+1}: {plate_text}")
            return plate_text

    print("[-] No plate detected.")
    return None

# Optional: For standalone testing
if __name__ == "__main__":
    plate = get_number_plate()
    if plate:
        print(f"Detected plate: {plate}")
        save_plate_to_db(plate)  # ✅ Store in database
    else:
        print("No plate detected.")
