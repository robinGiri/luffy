import requests
import logging
import psutil
import torch.multiprocessing as mp
import traceback
import pyaudio
import wave
import numpy as np
import noisereduce as nr
import speech_recognition as sr
import pyttsx3
import os
from flask import Flask, request, jsonify, send_from_directory
from threading import Thread
from moderation import contains_forbidden_words
from utils.text_generation import generate_text

mp.set_start_method('spawn', force=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

engine = pyttsx3.init()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/receive_audio', methods=['POST', 'GET'])
def receive_audio():
    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        return jsonify({"message": "File successfully received", "file_path": file_path}), 200

    elif request.method == 'GET':
        return jsonify({"message": "GET request received"}), 200

@app.route('/uploaded_files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

def log_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    logging.info(f"Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")

def record_audio(filename, duration=5, fs=44100):
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
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

def reduce_noise(input_file, output_file):
    with wave.open(input_file, 'rb') as wf:
        signal = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        frame_rate = wf.getframerate()
    
    reduced_noise_signal = nr.reduce_noise(y=signal, sr=frame_rate)
    
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(frame_rate)
        wf.writeframes(reduced_noise_signal.tobytes())

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

def speak_text(text, filename):
    engine.save_to_file(text, filename)
    engine.runAndWait()

def send_audio_to_api(file_path):
    url = 'http://localhost:5000/receive_audio'
    try:
        with open(file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            response = requests.post(url, files=files)
            response.raise_for_status()
            logging.info(f"API Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while sending the audio file: {e}")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    while True:
        try:
            audio_filename = "input.wav"
            noise_reduced_filename = "input_reduced.wav"
            avatar_directory = "avatar/resources/sounds"
            os.makedirs(avatar_directory, exist_ok=True)
            output_audio_filename = os.path.join(avatar_directory, "output_audio.wav")
            
            record_audio(audio_filename)
            
            reduce_noise(audio_filename, noise_reduced_filename)
            input_text = recognize_speech_from_file(noise_reduced_filename)

            logging.info(f"Recognized text: {input_text}")

            if input_text.lower() == 'exit':
                print("Exiting.")
                break

            if input_text:
                if contains_forbidden_words(input_text):
                    output_text = "Can't generate a response due to inappropriate content."
                else:
                    output_text = generate_text(input_text)

                logging.info(f"Generated text: {output_text}")
                speak_text(output_text, output_audio_filename)
                log_memory_usage()

                send_audio_to_api(output_audio_filename)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            logging.error(traceback.format_exc())
