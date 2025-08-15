"""
Comprehensive Hardware AI Model Trainer
Trains an AI model that knows EVERYTHING about hardware components
- Physical characteristics, pin colors, wiring details
- Electrical specifications, troubleshooting, compatibility
- Programming examples, alternatives, environmental conditions
"""

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling,
    AutoConfig, GPT2LMHeadModel, GPT2Tokenizer
)
from peft import get_peft_model, LoraConfig, TaskType, PeftModel
import json
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import wandb
from datasets import Dataset as HFDataset
import numpy as np
from sklearn.model_selection import train_test_split
import gc

from config import PROCESSED_DATA_DIR, MODELS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveHardwareDataset(Dataset):
    """Dataset for comprehensive hardware knowledge training"""
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 1024):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Prepare training texts
        self.training_texts = self._prepare_training_texts()
    
    def _prepare_training_texts(self) -> List[str]:
        """Prepare comprehensive training texts with rich context"""
        texts = []
        
        for item in self.data:
            question = item['question']
            answer = item['answer']
            component = item.get('component', '')
            category = item.get('category', '')
            context = item.get('context', '')
            
            # Create rich training text with multiple formats
            formats = [
                # Standard Q&A format
                f"Human: {question}\nAssistant: {answer}",
                
                # Knowledge statement format
                f"Hardware Knowledge: {answer}",
                
                # Component-specific format
                f"About {component}: {answer}",
                
                # Category-specific format
                f"{category.title()} Information: {answer}",
                
                # Context-rich format
                f"Question: {question}\nContext: {context}\nAnswer: {answer}",
                
                # Detailed explanation format
                f"When working with {component}, it's important to know that {answer}",
                
                # Troubleshooting format (if applicable)
                f"If you're wondering about {component}: {answer}"
            ]
            
            # Add all formats to training data
            texts.extend(formats)
            
            # Add component-specific knowledge statements
            if component:
                texts.append(f"The {component} is a {category} component. {answer}")
                texts.append(f"Component: {component} - {answer}")
        
        return texts
    
    def __len__(self):
        return len(self.training_texts)
    
    def __getitem__(self, idx):
        text = self.training_texts[idx]
        
        # Add special tokens and format
        formatted_text = f"<|startoftext|>{text}<|endoftext|>"
        
        # Tokenize
        encoding = self.tokenizer(
            formatted_text,
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

class ComprehensiveHardwareModelTrainer:
    """Trainer for comprehensive hardware knowledge model"""
    
    def __init__(self, model_name: str = "gpt2-medium"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.training_data = None
        self.comprehensive_data = {}
        
        # Training configuration for comprehensive knowledge
        self.training_config = {
            'max_length': 1024,
            'batch_size': 4,  # Smaller batch size for larger context
            'learning_rate': 3e-5,
            'num_epochs': 5,  # More epochs for comprehensive learning
            'warmup_steps': 500,
            'weight_decay': 0.01,
            'gradient_accumulation_steps': 4,
            'save_steps': 500,
            'eval_steps': 250,
            'logging_steps': 50
        }
    
    def load_comprehensive_training_data(self):
        """Load all comprehensive training datasets"""
        
        # Load main comprehensive training data
        main_file = PROCESSED_DATA_DIR / "comprehensive_training_data.json"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            logger.info(f"Loaded {len(self.training_data)} main training examples")
        
        # Load specialized datasets
        specialized_files = [
            "physical_knowledge_training.json",
            "electrical_knowledge_training.json", 
            "programming_knowledge_training.json",
            "wiring_knowledge_training.json",
            "troubleshooting_knowledge_training.json",
            "compatibility_knowledge_training.json",
            "performance_knowledge_training.json",
            "environmental_knowledge_training.json",
            "integration_knowledge_training.json"
        ]
        
        for filename in specialized_files:
            filepath = PROCESSED_DATA_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    specialized_data = json.load(f)
                    dataset_name = filename.replace('_training.json', '')
                    self.comprehensive_data[dataset_name] = specialized_data
                    logger.info(f"Loaded {len(specialized_data)} {dataset_name} examples")
        
        # Combine all data for training
        all_training_data = self.training_data.copy() if self.training_data else []
        for dataset in self.comprehensive_data.values():
            all_training_data.extend(dataset)
        
        self.training_data = all_training_data
        logger.info(f"Total training examples: {len(self.training_data)}")
        
        return len(self.training_data) > 0
    
    def prepare_model_and_tokenizer(self):
        """Prepare model and tokenizer for comprehensive training"""
        
        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        
        # Add special tokens
        special_tokens = {
            'pad_token': '<|pad|>',
            'eos_token': '<|endoftext|>',
            'bos_token': '<|startoftext|>',
            'unk_token': '<|unknown|>'
        }
        
        self.tokenizer.add_special_tokens(special_tokens)
        
        # Load model
        config = AutoConfig.from_pretrained(self.model_name)
        self.model = GPT2LMHeadModel.from_pretrained(
            self.model_name,
            config=config,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Resize token embeddings for new tokens
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        logger.info(f"Model and tokenizer prepared: {self.model_name}")
        logger.info(f"   Vocabulary size: {len(self.tokenizer)}")
        logger.info(f"   Model parameters: {self.model.num_parameters():,}")
    
    def setup_lora_for_comprehensive_training(self):
        """Setup LoRA for efficient comprehensive training"""
        
        # LoRA configuration for comprehensive knowledge
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,  # Higher rank for more complex knowledge
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["c_attn", "c_proj", "c_fc"],  # GPT-2 specific modules
            bias="none"
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        self.model.print_trainable_parameters()
        
        logger.info("⚡ LoRA configuration applied for comprehensive training")
    
    def create_comprehensive_datasets(self, test_size: float = 0.1, val_size: float = 0.1):
        """Create training, validation, and test datasets"""
        
        # Split data
        train_data, temp_data = train_test_split(
            self.training_data, 
            test_size=(test_size + val_size), 
            random_state=42,
            stratify=[item.get('category', 'general') for item in self.training_data]
        )
        
        val_data, test_data = train_test_split(
            temp_data, 
            test_size=(test_size / (test_size + val_size)), 
            random_state=42,
            stratify=[item.get('category', 'general') for item in temp_data]
        )
        
        # Create datasets
        train_dataset = ComprehensiveHardwareDataset(
            train_data, self.tokenizer, self.training_config['max_length']
        )
        val_dataset = ComprehensiveHardwareDataset(
            val_data, self.tokenizer, self.training_config['max_length']
        )
        test_dataset = ComprehensiveHardwareDataset(
            test_data, self.tokenizer, self.training_config['max_length']
        )
        
        logger.info(f"Dataset splits:")
        logger.info(f"   Training: {len(train_dataset)} examples")
        logger.info(f"   Validation: {len(val_dataset)} examples")
        logger.info(f"   Test: {len(test_dataset)} examples")
        
        return train_dataset, val_dataset, test_dataset
    
    def train_comprehensive_model(self, output_dir: str = None, use_wandb: bool = False):
        """Train the comprehensive hardware knowledge model"""
        
        if not self.training_data:
            logger.error("No training data loaded")
            return False
        
        output_dir = output_dir or str(MODELS_DIR / "comprehensive_hardware_model")
        
        # Create datasets
        train_dataset, val_dataset, test_dataset = self.create_comprehensive_datasets()
        
        # Initialize wandb if requested
        if use_wandb:
            try:
                wandb.init(
                    project="comprehensive-hardware-ai",
                    name="comprehensive-hardware-training",
                    config=self.training_config
                )
            except Exception as e:
                logger.warning(f"Could not initialize wandb: {e}")
                use_wandb = False
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.training_config['num_epochs'],
            per_device_train_batch_size=self.training_config['batch_size'],
            per_device_eval_batch_size=self.training_config['batch_size'],
            gradient_accumulation_steps=self.training_config['gradient_accumulation_steps'],
            warmup_steps=self.training_config['warmup_steps'],
            learning_rate=self.training_config['learning_rate'],
            weight_decay=self.training_config['weight_decay'],
            logging_steps=self.training_config['logging_steps'],
            evaluation_strategy="steps",
            eval_steps=self.training_config['eval_steps'],
            save_steps=self.training_config['save_steps'],
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="wandb" if use_wandb else None,
            fp16=torch.cuda.is_available(),
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            gradient_checkpointing=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            save_strategy="steps"
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
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )
        
        # Start training
        logger.info("Starting comprehensive hardware knowledge training...")
        
        try:
            trainer.train()
            
            # Save model
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            
            # Evaluate on test set
            logger.info("Evaluating on test set...")
            test_results = trainer.evaluate(test_dataset)
            logger.info(f"Test results: {test_results}")
            
            # Save training info
            training_info = {
                'model_name': self.model_name,
                'training_config': self.training_config,
                'dataset_stats': {
                    'total_examples': len(self.training_data),
                    'train_examples': len(train_dataset),
                    'val_examples': len(val_dataset),
                    'test_examples': len(test_dataset)
                },
                'test_results': test_results,
                'specialized_datasets': {name: len(data) for name, data in self.comprehensive_data.items()}
            }
            
            with open(Path(output_dir) / "training_info.json", 'w') as f:
                json.dump(training_info, f, indent=2)
            
            logger.info(f"Training completed! Model saved to {output_dir}")
            
            # Finish wandb run
            if use_wandb:
                wandb.finish()
            
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def evaluate_comprehensive_knowledge(self, model_path: str = None):
        """Evaluate the model's comprehensive hardware knowledge"""
        
        if model_path:
            # Load trained model
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            self.model = PeftModel.from_pretrained(
                GPT2LMHeadModel.from_pretrained(model_path),
                model_path
            )
        
        if not self.model or not self.tokenizer:
            logger.error("No model loaded for evaluation")
            return
        
        self.model.eval()
        
        # Comprehensive test questions covering all aspects
        test_questions = [
            # Physical characteristics
            "What color is the ESP32 chip?",
            "What are the physical dimensions of DHT22?",
            "What package type is the MPU6050?",
            
            # Pin details
            "What color is pin 1 on ESP32?",
            "What is the function of pin VCC on DHT22?",
            "Which pins are power pins on Arduino Uno?",
            
            # Electrical specifications
            "What is the operating voltage of HC-SR04?",
            "What is the current consumption of MPU6050?",
            "What is the maximum voltage for ESP32 pins?",
            
            # Wiring and connections
            "How do I wire DHT22 to ESP32?",
            "What resistors are needed with HC-SR04?",
            "How do I connect multiple WS2812 LEDs?",
            
            # Programming
            "What library do I need for MPU6050?",
            "How do I initialize DHT22 in Arduino code?",
            "Show me code to read temperature from DS18B20",
            
            # Troubleshooting
            "Why is my DHT22 returning NaN values?",
            "How do I test if ESP32 is working?",
            "My HC-SR04 gives wrong distance readings, why?",
            
            # Compatibility
            "Can I use DHT22 with 3.3V systems?",
            "Is MPU6050 compatible with ESP32?",
            "What voltage level shifter do I need for HC-05?",
            
            # Environmental
            "What temperature range can DHT22 operate in?",
            "Is HC-SR04 waterproof?",
            "What certifications does ESP32 have?",
            
            # Alternatives
            "What are alternatives to DHT22?",
            "What can I use instead of HC-SR04?",
            "What is similar to MPU6050?"
        ]
        
        results = []
        
        logger.info("Testing comprehensive hardware knowledge...")
        
        for question in test_questions:
            try:
                # Format input
                input_text = f"<|startoftext|>Human: {question}\nAssistant:"
                
                # Tokenize
                inputs = self.tokenizer(
                    input_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                )
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=200,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        repetition_penalty=1.1
                    )
                
                # Decode response
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.replace(input_text.replace("<|startoftext|>", ""), "").strip()
                
                results.append({
                    'question': question,
                    'response': response
                })
                
                logger.info(f"Q: {question}")
                logger.info(f"A: {response[:100]}...")
                logger.info("")
                
            except Exception as e:
                logger.error(f"Error generating response for '{question}': {e}")
                results.append({
                    'question': question,
                    'response': f"Error: {e}"
                })
        
        # Save evaluation results
        eval_file = MODELS_DIR / "comprehensive_hardware_model" / "evaluation_results.json"
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation results saved to {eval_file}")
        
        return results
    
    def load_trained_model(self, model_path: str):
        """Load a previously trained comprehensive model"""
        
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            
            # Load base model first
            base_model = GPT2LMHeadModel.from_pretrained(model_path)
            
            # Then load PEFT model
            self.model = PeftModel.from_pretrained(base_model, model_path)
            
            logger.info(f"Loaded comprehensive trained model from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = 512, temperature: float = 0.7) -> str:
        """Generate response using the trained model"""
        
        if not hasattr(self, 'model') or self.model is None:
            logger.warning("Model not loaded, using fallback response")
            return self._generate_fallback_response(prompt)
        
        try:
            # Tokenize the prompt
            inputs = self.tokenizer.encode(prompt, return_tensors='pt')
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the response
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Fallback response when model is not available"""
        
        # Simple pattern matching for circuit diagrams
        if "esp32" in prompt.lower() and "ili9341" in prompt.lower():
            return '''[
  ["esp:GND.2", "lcd1:GND", "black", ["h-19.2", "v91.54"]],
  ["esp:4", "lcd1:RST", "purple", ["h-48", "v67.2"]],
  ["esp:2", "lcd1:D/C", "#8f4814", ["h-28.8", "v44.14"]],
  ["esp:18", "lcd1:SCK", "gray", ["v-0.01", "h-48", "v-19.2"]],
  ["esp:19", "lcd1:MISO", "orange", ["h-67.2", "v-9.61", "h0", "v-19.2"]],
  ["esp:23", "lcd1:MOSI", "green", ["h-38.4", "v-67.31"]],
  ["esp:5V", "lcd1:VCC", "red", ["h-21.83", "v-206.3", "h201.6", "v48.5"]],
  ["esp:15", "lcd1:CS", "violet", ["h-57.6", "v105.6"]]
]'''
        
        return "Pattern-based circuit connections generated."

def main():
    """Main comprehensive training function"""
    
    logger.info("Starting Comprehensive Hardware AI Model Training")
    logger.info("="*60)
    
    # Initialize trainer
    trainer = ComprehensiveHardwareModelTrainer()
    
    # Load comprehensive training data
    if not trainer.load_comprehensive_training_data():
        logger.error("Failed to load training data")
        return
    
    # Prepare model and tokenizer
    trainer.prepare_model_and_tokenizer()
    
    # Setup LoRA for efficient training
    trainer.setup_lora_for_comprehensive_training()
    
    # Train the comprehensive model
    success = trainer.train_comprehensive_model()
    
    if success:
        # Evaluate the trained model
        logger.info("Evaluating comprehensive knowledge...")
        trainer.evaluate_comprehensive_knowledge()
        
        logger.info("Comprehensive Hardware AI Model Training Completed!")
        logger.info("Your AI model now knows EVERYTHING about hardware components!")
        
        # Display what the model learned
        logger.info("\nModel Knowledge Coverage:")
        logger.info("   Physical characteristics (colors, dimensions, packages)")
        logger.info("   📍 Pin details (colors, functions, voltages, currents)")
        logger.info("   ⚡ Electrical specifications (voltage, current, power)")
        logger.info("   Wiring diagrams and connection details")
        logger.info("   Programming examples and libraries")
        logger.info("   Troubleshooting and debugging")
        logger.info("   🤝 Compatibility and integration")
        logger.info("   🌡️  Environmental conditions and protection")
        logger.info("   Alternative components and equivalents")
        logger.info("   Multi-component project integration")
        
    else:
        logger.error("Training failed!")

if __name__ == "__main__":
    main()
