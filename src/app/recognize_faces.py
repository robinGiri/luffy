import cv2
import pickle
import os
import numpy as np
import face_recognition
import speech_recognition as sr
import pyttsx3
import threading
import queue
from scipy.signal import medfilt
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from deepface import DeepFace

# Load pre-trained model and tokenizer
model_name = "gpt2"  # You can use "gpt2-medium", "gpt2-large", "gpt2-xl" for larger models
gpt_model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Ensure padding token is set correctly
tokenizer.pad_token = tokenizer.eos_token

def noise_cancellation(audio_data, sampling_rate):
    filtered_audio = medfilt(audio_data, kernel_size=3)
    return filtered_audio

def train_model(data_dir="data", model_save_path="models/face_recognition_model.pkl"):
    if os.path.exists(model_save_path):
        with open(model_save_path, "rb") as f:
            existing_model = pickle.load(f)
        known_encodings = existing_model["encodings"]
        known_names = existing_model["names"]
    else:
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

def capture_images(person_name, save_dir="data", max_images=50):
    cap = cv2.VideoCapture(0)
    person_dir = os.path.join(save_dir, person_name)
    os.makedirs(person_dir, exist_ok=True)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    count = 0
    while count < max_images:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            face_img = frame[y:y+h, x:x+w]
            img_path = os.path.join(person_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face_img)
            count += 1
            print(f"Image {count} captured")

        cv2.imshow("Capturing Images - Press 'q' to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images for {person_name}")
    train_model()
    recognize_faces()

def recognize_faces(model_path="models/face_recognition_model.pkl"):
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}")
        return

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("Error: Could not open video capture")
        return

    print("Starting video capture. Press 'q' to quit. Say 'capture' to start capturing images.")

    engine = pyttsx3.init()
    
    recognized_names = []
    speech_queue = queue.Queue()
    capture_queue = queue.Queue()

    def recognize_speech():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        while True:
            with mic as source:
                print("Listening for commands...")
                audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                sample_rate = audio.sample_rate
                audio_data = noise_cancellation(audio_data, sample_rate)
                audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
                
                speech_text = recognizer.recognize_google(audio)
                print(f"Recognized Speech: {speech_text}")
                speech_queue.put(speech_text.lower())
            except sr.UnknownValueError:
                print("Speech could not be recognized")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service: {e}")


    def generate_response(prompt, max_length=100):
        inputs = tokenizer.encode(prompt, return_tensors='pt')
        attention_mask = inputs.ne(tokenizer.pad_token_id).long()
        outputs = gpt_model.generate(
            inputs,
            max_length=max_length,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=attention_mask,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True,
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def handle_greeting():
        while True:
            speech_text = speech_queue.get()
            print(f"Processing speech: {speech_text}")
            response = generate_response(speech_text)
            print(f"AI Response: {response}")
            engine.say(response)
            engine.runAndWait()

    def process_frame():
        nonlocal recognized_names
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture image")
            return None, None, None
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        current_names = []
        emotions = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(model["encodings"], face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(model["encodings"], face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = model["names"][best_match_index]
            
            current_names.append(name)

        recognized_names = current_names

        for (top, right, bottom, left), name in zip(face_locations, recognized_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            face_frame = frame[top:bottom, left:right]
            try:
                analysis = DeepFace.analyze(face_frame, actions=['emotion'], enforce_detection=False)
                emotion = analysis[0]['dominant_emotion']
                emotions.append(emotion)
            except Exception as e:
                emotions.append(None)
                print(f"Emotion detection error: {e}")

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, f"{name} - {emotions[-1]}", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame, recognized_names, emotions

    def get_person_name():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        while True:
            with mic as source:
                print("Listening for the person's name...")
                audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                sample_rate = audio.sample_rate
                audio_data = noise_cancellation(audio_data, sample_rate)
                audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
                speech_text = recognizer.recognize_google(audio)
                print(f"Recognized Name: {speech_text}")
                return speech_text
            except sr.UnknownValueError:
                print("Name could not be recognized. Please try again.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service: {e}")
                return None

    speech_thread = threading.Thread(target=recognize_speech)
    greeting_thread = threading.Thread(target=handle_greeting)
    speech_thread.daemon = True
    greeting_thread.daemon = True
    speech_thread.start()
    greeting_thread.start()

    while True:
        frame, recognized_names, emotions = process_frame()

        if frame is not None:
            cv2.imshow("Recognize Faces - Press 'q' to quit", frame)

        if not capture_queue.empty():
            command = capture_queue.get()
            if command == "start_capture":
                person_name = get_person_name()
                if person_name:
                    capture_images(person_name)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
