import argparse
import wandb
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, prepare_model_for_kbit_training
from model_env import *
from trl import SFTTrainer

train_dataset = load_dataset("csv", data_files="../train/train.csv").shuffle()
valid_dataset = load_dataset("csv", data_files="../valid/valid.csv")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.add_eos_token = True

model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, quantization_config=bnb_config, device_map='auto')
model = prepare_model_for_kbit_training(model)

model.config.use_cache = False  # enable using cache when inference

peft_config = LoraConfig(
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    r=LORA_RANK,
    bias=LORA_BIAS,
    task_type=LORA_TASK_TYPE,

)

wandb.login(key="ab2c9010235c59b6958c5c7ab86531ebbadb17ac")
run_train = wandb.init(project=WANDB_TRAINING_TITLE, job_type="training", anonymous="allow")
run_valid = wandb.init(project=WANDB_VALID_TITLE, job_type="evaluation", anonymous="allow")

training_args = TrainingArguments(
    output_dir="models",
    num_train_epochs=5,
    per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=PER_DEVICE_VALID_BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    optim='paged_adamw_8bit',
    learning_rate=LEARNING_RATE,
    save_strategy="epoch",
    logging_steps=30,
    weight_decay=0.001,
    fp16=True,
    max_grad_norm=0.3,
    warmup_ratio=0.01,
    report_to="wandb",
    lr_scheduler_type="cosine",
)
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    dataset_text_field='prompt',
    max_seq_length=MAX_LENGTH,
    tokenizer=tokenizer,
    args=training_args,
    packing=True,
    peft_config=peft_config
)
trainer.train()
trainer.save_model("models/8B_1v")
