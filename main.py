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
import os
from moderation import contains_forbidden_words

mp.set_start_method('spawn', force=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

engine = pyttsx3.init()

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

def save_speech_to_audio(text, filename):
    engine.save_to_file(text, filename)
    engine.runAndWait()

if __name__ == "__main__":
    try:
        log_memory_usage() 
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

                print(f"Recognized text: {input_text}")

                if input_text.lower() == 'exit':
                    break
                if input_text:
                    if contains_forbidden_words(input_text):
                        output_text = "Can't generate a response due to inappropriate content."
                    else:
                        output_text = generate_text(input_text)

                    print(output_text)
                    speak_text(output_text)
                    save_speech_to_audio(output_text, output_audio_filename)
                    log_memory_usage()

            except Exception as e:
                logging.error(f"An error occurred in the main loop: {e}")
                logging.error(traceback.format_exc())
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
