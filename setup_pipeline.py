#!/usr/bin/env python3
"""
Complete pipeline script for the AI Hardware Understanding System
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_collector import DataCollector
from data_processor import DataProcessor
from vector_database import load_and_index_data
from model_trainer import HardwareModelTrainer, create_training_data_for_huggingface

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_data_collection():
    """Step 1: Collect hardware data from various sources"""
    logger.info("Starting data collection...")
    
    try:
        collector = DataCollector()
        
        # Check if data already exists
        existing_data = collector.load_collected_data()
        
        if not existing_data:
            logger.info("Collecting new hardware data...")
            collected_data = await collector.collect_all_data()
            collector.save_collected_data(collected_data)
            logger.info("Data collection completed!")
        else:
            logger.info("Using existing collected data")
        
        return True
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        return False

def run_data_processing():
    """Step 2: Process raw data for training and RAG"""
    logger.info("Starting data processing...")
    
    try:
        processor = DataProcessor()
        
        # Load raw data
        raw_data = processor.load_raw_data()
        
        if not raw_data:
            logger.error("No raw data found. Please run data collection first.")
            return False
        
        # Process all data
        processed_data, qa_pairs, embeddings_data = processor.process_all_data(raw_data)
        
        # Save processed data
        processor.save_processed_data(processed_data, qa_pairs, embeddings_data)
        
        logger.info("Data processing completed!")
        return True
        
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        return False

def setup_vector_database():
    """Step 3: Setup vector database for RAG"""
    logger.info("🗄️ Setting up vector database...")
    
    try:
        vector_db = load_and_index_data()
        
        if vector_db:
            stats = vector_db.get_database_stats()
            logger.info(f"Vector database ready with {stats['total_documents']} documents")
            logger.info(f"   Components: {len(stats['components'])}")
            logger.info(f"   Categories: {len(stats['categories'])}")
            return True
        else:
            logger.error("Failed to setup vector database")
            return False
            
    except Exception as e:
        logger.error(f"Vector database setup failed: {e}")
        return False

def run_model_training(skip_if_exists=True):
    """Step 4: Fine-tune the model"""
    logger.info("Starting model training...")
    
    try:
        from config import MODELS_DIR
        
        model_path = MODELS_DIR / "hardware_model"
        
        if skip_if_exists and model_path.exists():
            logger.info("Using existing trained model")
            return True
        
        # Create HuggingFace dataset
        create_training_data_for_huggingface()
        
        # Initialize trainer
        trainer = HardwareModelTrainer()
        
        # Load data
        if not trainer.load_data():
            logger.error("Failed to load training data")
            return False
        
        # Prepare model
        trainer.prepare_model()
        
        # Setup LoRA for efficient training
        trainer.setup_lora()
        
        # Train model
        trainer.train(use_wandb=False)  # Disable wandb for automated runs
        
        # Quick evaluation
        trainer.evaluate_model()
        
        logger.info("Model training completed!")
        return True
        
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        logger.info("You can still use the RAG system without the fine-tuned model")
        return False

async def run_complete_pipeline():
    """Run the complete AI system setup pipeline"""
    logger.info("Starting AI Hardware Understanding System setup...")
    
    # Step 1: Data Collection
    success = await run_data_collection()
    if not success:
        logger.error("Pipeline failed at data collection step")
        return False
    
    # Step 2: Data Processing
    success = run_data_processing()
    if not success:
        logger.error("Pipeline failed at data processing step")
        return False
    
    # Step 3: Vector Database Setup
    success = setup_vector_database()
    if not success:
        logger.error("Pipeline failed at vector database setup")
        return False
    
    # Step 4: Model Training (optional, can fail and still work)
    success = run_model_training(skip_if_exists=True)
    if not success:
        logger.warning("Model training failed, but RAG system should still work")
    
    logger.info("AI Hardware Understanding System setup completed!")
    logger.info("🌐 You can now run the application with: python src/app.py")
    
    return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Hardware Understanding System Pipeline")
    parser.add_argument("--step", choices=["collect", "process", "vector", "train", "all"], 
                       default="all", help="Run specific pipeline step")
    parser.add_argument("--force-train", action="store_true", 
                       help="Force model training even if model exists")
    
    args = parser.parse_args()
    
    if args.step == "collect":
        asyncio.run(run_data_collection())
    elif args.step == "process":
        run_data_processing()
    elif args.step == "vector":
        setup_vector_database()
    elif args.step == "train":
        run_model_training(skip_if_exists=not args.force_train)
    else:  # "all"
        asyncio.run(run_complete_pipeline())

if __name__ == "__main__":
    main()
