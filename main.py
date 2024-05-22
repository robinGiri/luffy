from src.app.capture_images import capture_images
from src.app.train_model import train_model
from src.app.recognize_faces import recognize_faces

if __name__ == "__main__":
    choice = input("Choose an option:\n1. Capture Images\n2. Train Model\n3. Recognize Faces\n")
    if choice == '1':
        person_name = input("Enter the name of the person: ")
        capture_images(person_name)
    elif choice == '2':
        train_model()
    elif choice == '3':
        recognize_faces()
    else:
        print("Invalid choice!")
