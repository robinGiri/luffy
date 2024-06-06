import yaml
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from prompts.prompt_templates import get_prompt_template
import logging

def load_model(config_path="config/config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    model_name = config['model_name']
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    return model

def load_tokenizer(config_path="config/config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    model_name = config['model_name']
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    return tokenizer

def generate_text(input_text, config_path="config/config.yaml"):
    try:
        # Load configuration
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        logging.info("Loading model...")
        model = load_model(config_path)
        logging.info("Loading tokenizer...")
        tokenizer = load_tokenizer(config_path)
        prompt_template = get_prompt_template()

        # Prepare the input prompt using the template
        prompt = prompt_template.format(input=input_text)

        # Tokenize the input
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs.input_ids
        attention_mask = inputs.attention_mask

        # Generate text with specified parameters
        logging.info("Generating text...")
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=config['max_length'],
            do_sample=True,
            top_k=config['top_k'],
            top_p=config['top_p'],
            pad_token_id=tokenizer.eos_token_id  # Set the pad token ID to eos_token_id
        )

        # Decode and return the output text
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        logging.error(f"An error occurred during text generation: {e}")
        raise
