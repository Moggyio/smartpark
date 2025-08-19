import cv2
import easyocr
import torch
import os

# Load YOLO model once when the script is imported
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'])

def get_number_plate():
    """
    Detects and reads a number plate from test_plate.jpeg.
    Returns:
        plate_text (str) if found, else None
    """
    # Resolve image path
    base_dir = os.path.dirname(__file__)
    img_path = os.path.abspath(os.path.join(base_dir, '..', 'test_plate.jpeg'))

    # Load image
    img = cv2.imread(img_path)
    if img is None:
        print("[-] Could not load image.")
        return None

    # Run YOLO detection
    results = model(img)

    # Ensure output directory exists
    os.makedirs("plate_outputs", exist_ok=True)

    # Process detections
    for i, (*box, conf, cls) in enumerate(results.xyxy[0]):
        x1, y1, x2, y2 = map(int, box)
        cropped = img[y1:y2, x1:x2]
        cv2.imwrite(f"plate_outputs/plate_{i}.jpg", cropped)

        # OCR on cropped image
        ocr_result = reader.readtext(cropped)
        if ocr_result:
            plate_text = ocr_result[0][-2]
            print(f"[+] Detected Plate #{i+1}: {plate_text}")
            return plate_text  # Return the first detected plate

    print("[-] No plate detected.")
    return None


# Optional: For standalone testing
if __name__ == "__main__":
    plate = get_number_plate()
    if plate:
        print(f"Detected plate: {plate}")
    else:
        print("No plate detected.")
