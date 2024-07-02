import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer, SFTConfig

# Load new dataset from a .txt file
dataset_path = 'data/dataset.txt'
dataset = load_dataset('text', data_files={'train': dataset_path}, split='train')

# Verify the dataset
print(dataset)

# Model and tokenizer configuration
model_name = "luffyAI/ChildModel-02"
max_length = 50
top_k = 50
top_p = 0.95

# Load tokenizer and model without 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(model_name)
model.config.use_cache = False
model.config.pretraining_tp = 1

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Load LoRA configuration
peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

# Set training parameters with reduced batch size
training_arguments = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=1,  # Reduced batch size
    gradient_accumulation_steps=4,  # Accumulate gradients to keep effective batch size
    optim="paged_adamw_32bit",
    save_steps=0,
    logging_steps=25,
    learning_rate=2e-4,
    weight_decay=0.001,
    fp16=False,
    bf16=False,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="cosine",
    report_to="tensorboard"
)

# Initialize the SFTTrainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_arguments,
    peft_config=peft_config,
    dataset_text_field="text",
    max_seq_length=None,
    packing=False
)

# Train model
trainer.train()

# Save trained model
new_model_name = "luffyAI/ChildModel-02-finetuned"
trainer.model.save_pretrained(new_model_name)
tokenizer.save_pretrained(new_model_name)

# Use the text generation pipeline with the fine-tuned model
pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=max_length, top_k=top_k, top_p=top_p)
prompt = "Give me a children story"
result = pipe(prompt)
print(result[0]['generated_text'])

# Empty VRAM
del model
del pipe
del trainer
import gc
gc.collect()
gc.collect()
