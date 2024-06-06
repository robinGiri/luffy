from transformers import GPTNeoForCausalLM
import yaml

def load_model(config_path="config/config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    model_name = config['model_name']
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    return model
