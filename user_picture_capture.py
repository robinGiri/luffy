import logging
import pyaudio
import wave
import numpy as np
import speech_recognition as sr
import cv2
import traceback
import os
import pyttsx3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(duration=5, fs=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True, frames_per_buffer=1024)
    frames = []
    logging.info("Listening...")
    for _ in range(0, int(fs / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    logging.info("Listening finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open("input.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return "input.wav"

def recognize_speech_from_file(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio)
        logging.info(f"Recognized text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Listening for user's name...")
        audio = recognizer.listen(source)
    try:
        name = recognizer.recognize_google(audio)
        logging.info(f"Recognized name: {name}")
        return name
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def capture_images(person_name, num_images=30, directory="training_data"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    person_dir = os.path.join(directory, person_name)
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Could not open webcam")
        return
    
    logging.info("Webcam opened successfully")
    for i in range(num_images):
        ret, frame = cap.read()
        if ret:
            filename = os.path.join(person_dir, f"{person_name}_{i+1}.jpg")
            cv2.imwrite(filename, frame)
            logging.info(f"Image captured and saved as {filename}")
        else:
            logging.error("Failed to capture image")
    
    cap.release()
    cv2.destroyAllWindows()
    
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
def check_for_termination(audio_text):
    return "thank you" in audio_text.lower()

if __name__ == "__main__":
    try:
        while True:
            try:
                logging.info("Starting new audio recording")
                audio_filename = record_audio()
                logging.info("Audio recording complete")
                
                logging.info("Starting speech recognition")
                recognized_text = recognize_speech_from_file(audio_filename)
                logging.info(f"Speech recognized: {recognized_text}")
                
                if check_for_termination(recognized_text):
                    speak_text("Have a nice day!")
                    logging.info("Terminating program on user's request.")
                    break
                
                if "recognize" in recognized_text or "me" in recognized_text:
                    logging.info("Keywords detected, initiating image capture")
                    
                    # Ask for the user's name
                    logging.info("Asking for the user's name")
                    speak_text("Hello! What is your name?")
                    print("What is your name?")
                    user_name = recognize_speech_from_mic()
                    
                    if user_name:
                        capture_images(person_name=user_name, num_images=30)
                    else:
                        logging.error("No name recognized, skipping image capture")
                
            except Exception as e:
                logging.error(f"An error occurred in the main loop: {e}")
                logging.error(traceback.format_exc())
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
