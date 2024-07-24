import logging
import psutil
from utils.text_generation import generate_text
import torch.multiprocessing as mp
import traceback
import pyaudio
import wave
import numpy as np
import noisereduce as nr
import speech_recognition as sr
import pyttsx3
from moderation import contains_forbidden_words
from flask import Flask, request, jsonify
from flask_cors import CORS

mp.set_start_method('spawn', force=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

engine = pyttsx3.init()
app = Flask(__name__)
CORS(app)

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
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def reduce_noise(input_file, output_file):
    wf = wave.open(input_file, 'rb')
    signal = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    frame_rate = wf.getframerate()
    wf.close()
    
    reduced_noise_signal = nr.reduce_noise(y=signal, sr=frame_rate)
    
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(frame_rate)
    wf.writeframes(reduced_noise_signal.tobytes())
    wf.close()

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

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

@app.route('/process_input', methods=['POST'])
def process_input():
    try:
        data = request.get_json()
        input_text = data.get('input_text', '')
        
        if input_text.lower() == 'exit':
            return jsonify({"message": "Exiting"}), 200
        
        if input_text:
            if contains_forbidden_words(input_text):
                output_text = "Can't generate a response due to inappropriate content."
            else:
                output_text = generate_text(input_text)

            speak_text(output_text)
            log_memory_usage()
            return jsonify({"output_text": output_text}), 200
        else:
            return jsonify({"message": "No input text provided"}), 400

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
