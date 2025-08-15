"""
Fine-tuning module for training the hardware understanding model
"""

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
import json
import pandas as pd
from typing import Dict, List, Any
import logging
from pathlib import Path
import wandb
from datasets import Dataset as HFDataset

from config import MODEL_CONFIG, PROCESSED_DATA_DIR, MODELS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardwareQADataset(Dataset):
    """Dataset for hardware Q&A fine-tuning"""
    
    def __init__(self, qa_data: List[Dict], tokenizer, max_length: int = 512):
        self.qa_data = qa_data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.qa_data)
    
    def __getitem__(self, idx):
        item = self.qa_data[idx]
        
        # Format as conversational format
        text = f"Human: {item['question']}\nAssistant: {item['answer']}"
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }

class HardwareModelTrainer:
    """Trainer for hardware understanding model"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or MODEL_CONFIG['fine_tune_model']
        self.tokenizer = None
        self.model = None
        self.training_data = None
        
    def load_data(self, qa_file: str = "qa_pairs.json"):
        """Load Q&A data for training"""
        
        data_path = PROCESSED_DATA_DIR / qa_file
        
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            
            logger.info(f"Loaded {len(self.training_data)} Q&A pairs")
        else:
            logger.error(f"Training data not found: {data_path}")
            return False
        
        return True
    
    def prepare_model(self):
        """Prepare model and tokenizer for training"""
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Resize token embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        logger.info(f"Model and tokenizer loaded: {self.model_name}")
    
    def setup_lora(self):
        """Setup LoRA for efficient fine-tuning"""
        
        # LoRA configuration
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        self.model.print_trainable_parameters()
        
        logger.info("LoRA configuration applied")
    
    def prepare_datasets(self, train_split: float = 0.8):
        """Prepare training and validation datasets"""
        
        # Split data
        split_idx = int(len(self.training_data) * train_split)
        train_data = self.training_data[:split_idx]
        val_data = self.training_data[split_idx:]
        
        # Create datasets
        train_dataset = HardwareQADataset(train_data, self.tokenizer, MODEL_CONFIG['max_length'])
        val_dataset = HardwareQADataset(val_data, self.tokenizer, MODEL_CONFIG['max_length'])
        
        logger.info(f"Training samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")
        
        return train_dataset, val_dataset
    
    def train(self, output_dir: str = None, use_wandb: bool = True):
        """Train the model"""
        
        if not self.training_data:
            logger.error("No training data loaded")
            return
        
        output_dir = output_dir or str(MODELS_DIR / "hardware_model")
        
        # Prepare datasets
        train_dataset, val_dataset = self.prepare_datasets()
        
        # Initialize wandb if requested
        if use_wandb:
            try:
                wandb.init(
                    project="hardware-understanding",
                    name="fine-tune-hardware-model",
                    config=MODEL_CONFIG
                )
            except Exception as e:
                logger.warning(f"Could not initialize wandb: {e}")
                use_wandb = False
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=MODEL_CONFIG['num_epochs'],
            per_device_train_batch_size=MODEL_CONFIG['batch_size'],
            per_device_eval_batch_size=MODEL_CONFIG['batch_size'],
            warmup_steps=MODEL_CONFIG['warmup_steps'],
            learning_rate=MODEL_CONFIG['learning_rate'],
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            save_steps=500,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="wandb" if use_wandb else None,
            fp16=torch.cuda.is_available(),
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            gradient_checkpointing=True
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator
        )
        
        # Start training
        logger.info("Starting training...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Finish wandb run
        if use_wandb:
            wandb.finish()
        
        logger.info(f"Training completed. Model saved to {output_dir}")
    
    def evaluate_model(self, test_questions: List[str] = None):
        """Evaluate the trained model"""
        
        if test_questions is None:
            test_questions = [
                "What pins does ESP32 have?",
                "How do I connect DHT22 to Arduino?",
                "What is the voltage requirement for HC-SR04?",
                "Show me code example for MPU6050",
                "How to wire WS2812 LED strip?"
            ]
        
        if self.model is None or self.tokenizer is None:
            logger.error("Model not loaded")
            return
        
        self.model.eval()
        
        results = []
        
        for question in test_questions:
            # Format input
            input_text = f"Human: {question}\nAssistant:"
            
            # Tokenize
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(input_text, "").strip()
            
            results.append({
                'question': question,
                'response': response
            })
            
            logger.info(f"Q: {question}")
            logger.info(f"A: {response}\n")
        
        return results
    
    def load_trained_model(self, model_path: str):
        """Load a previously trained model"""
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        logger.info(f"Loaded trained model from {model_path}")

def create_training_data_for_huggingface():
    """Convert Q&A data to HuggingFace dataset format"""
    
    # Load Q&A data
    qa_file = PROCESSED_DATA_DIR / "qa_pairs.json"
    
    if not qa_file.exists():
        logger.error("Q&A data not found")
        return None
    
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    # Convert to HuggingFace format
    hf_data = []
    
    for item in qa_data:
        hf_data.append({
            'text': f"Human: {item['question']}\nAssistant: {item['answer']}",
            'component': item['component'],
            'category': item['category'],
            'data_type': item['data_type']
        })
    
    # Create dataset
    dataset = HFDataset.from_list(hf_data)
    
    # Save dataset
    dataset.save_to_disk(str(PROCESSED_DATA_DIR / "hf_dataset"))
    
    logger.info(f"Created HuggingFace dataset with {len(hf_data)} examples")
    
    return dataset

def main():
    """Main training function"""
    
    # Initialize trainer
    trainer = HardwareModelTrainer()
    
    # Load data
    if not trainer.load_data():
        return
    
    # Prepare model
    trainer.prepare_model()
    
    # Setup LoRA for efficient training
    trainer.setup_lora()
    
    # Train model
    trainer.train()
    
    # Evaluate model
    trainer.evaluate_model()
    
    logger.info("Training pipeline completed!")

if __name__ == "__main__":
    main()
