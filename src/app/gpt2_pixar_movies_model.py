import os
import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# Load pre-trained GPT-2 model and tokenizer
model_name = "gpt2"  # You can use "gpt2-medium", "gpt2-large", "gpt2-xl" for larger models
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Ensure padding token is set correctly
tokenizer.pad_token = tokenizer.eos_token

# Define the path to the CSV dataset
csv_file_path = "./datasets/PixarMovies.csv"

# Load and prepare dataset
def load_csv_dataset(file_path, tokenizer, block_size=128):
    df = pd.read_csv(file_path)
    texts = df['Movie'].tolist()  # Modify this line to extract other relevant columns if needed

    # Optionally, create synthetic descriptions
    descriptions = []
    for index, row in df.iterrows():
        description = f"{row['Movie']} ({row['Year Released']}): A {row['Length']} minute long movie with an IMDB score of {row['IMDB Score']}."
        descriptions.append(description)

    temp_txt_file = 'temp_dataset.txt'
    with open(temp_txt_file, 'w') as f:
        for text in descriptions:
            f.write(text + '\n')

    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=temp_txt_file,
        block_size=block_size
    )
    os.remove(temp_txt_file)  # Clean up the temporary file
    return dataset

# Create a data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Prepare training arguments
training_args = TrainingArguments(
    output_dir="./models/gpt2_pixar_movies_model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
)

# Ensure the dataset path exists
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"Dataset file {csv_file_path} not found. Please provide the correct path.")

# Load your dataset
dataset = load_csv_dataset(csv_file_path, tokenizer)

# Create the Trainer instance
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)

# Train the model
trainer.train()

# Save the model
trainer.save_model("./models/gpt2_pixar_movies_model")
