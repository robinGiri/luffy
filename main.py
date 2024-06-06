import logging
import psutil
from utils.text_generation import generate_text
import torch.multiprocessing as mp

# Set start method to 'spawn' for compatibility and avoid resource tracking issues
mp.set_start_method('spawn')

# Configure logging
logging.basicConfig(level=logging.INFO)

def log_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    logging.info(f"Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")

if __name__ == "__main__":
    try:
        log_memory_usage()
        while True:
            input_text = input("Enter your question (or 'exit' to quit): ")
            if input_text.lower() == 'exit':
                break
            output_text = generate_text(input_text)
            print(output_text)
            log_memory_usage()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
