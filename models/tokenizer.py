from transformers import GPT2Tokenizer
import yaml

def load_tokenizer(config_path="config/config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    model_name = config['model_name']
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    return tokenizer
