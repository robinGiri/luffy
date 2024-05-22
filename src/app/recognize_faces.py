import cv2
import pickle
import os
import numpy as np
import face_recognition
import speech_recognition as sr
import pyttsx3
import threading
import queue
from deepface import DeepFace

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

    print("Starting video capture. Press 'q' to quit.")

    engine = pyttsx3.init()
    
    recognized_names = []
    speech_queue = queue.Queue()

    def recognize_speech():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        while True:
            with mic as source:
                print("Listening for 'hello' or 'hi'...")
                audio = recognizer.listen(source, phrase_time_limit=3)
            try:
                speech_text = recognizer.recognize_google(audio)
                print(f"Recognized Speech: {speech_text}")
                speech_queue.put(speech_text.lower())
            except sr.UnknownValueError:
                print("Speech could not be recognized")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service: {e}")

    def greet_user(name, emotion=None):
        greeting = f"Hello, {name}!"
        if emotion:
            greeting += f" You seem to be {emotion}."
        engine.say(greeting)
        engine.runAndWait()

    def greet_unknown(emotion=None):
        greeting = "Hey there!"
        if emotion:
            greeting += f" You seem to be {emotion}."
        engine.say(greeting)
        engine.runAndWait()

    def handle_greeting():
        while True:
            speech_text = speech_queue.get()
            print(f"Processing speech: {speech_text}")
            if "hello" in speech_text or "hi" in speech_text:
                if recognized_names:
                    for name in recognized_names:
                        if name != "Unknown":
                            threading.Thread(target=greet_user, args=(name,)).start()
                            break
                else:
                    threading.Thread(target=greet_unknown).start()

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
                print(f"Emotion analysis: {analysis}")
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

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
