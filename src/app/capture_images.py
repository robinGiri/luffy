import cv2
import os

def capture_images(person_name, save_dir="data", max_images=50):
    cap = cv2.VideoCapture(0)
    person_dir = os.path.join(save_dir, person_name)
    os.makedirs(person_dir, exist_ok=True)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    capturing = False
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Capture Images - Press 'c' to start capturing, 'q' to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            capturing = True

        if capturing and count < max_images:
            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                img_path = os.path.join(person_dir, f"{count}.jpg")
                cv2.imwrite(img_path, face_img)
                count += 1
                print(f"Image {count} captured")
                if count >= max_images:
                    capturing = False
                    print("Finished capturing images")
                    break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images for {person_name}")

if __name__ == "__main__":
    person_name = input("Enter the name of the person: ")
    capture_images(person_name)
