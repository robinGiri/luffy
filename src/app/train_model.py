import face_recognition
import os
import pickle

def train_model(data_dir="data", model_save_path="models/face_recognition_model.pkl"):
    known_encodings = []
    known_names = []

    for person_name in os.listdir(data_dir):
        person_dir = os.path.join(data_dir, person_name)
        if not os.path.isdir(person_dir):
            continue

        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)

    model = {"encodings": known_encodings, "names": known_names}
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    with open(model_save_path, "wb") as f:
        pickle.dump(model, f)
    print("Model trained and saved at:", model_save_path)

if __name__ == "__main__":
        train_model()
