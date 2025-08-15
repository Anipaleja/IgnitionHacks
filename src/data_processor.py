"""
Data processing module for preparing training data
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
import numpy as np
from datasets import Dataset
import logging

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, HARDWARE_COMPONENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Process raw hardware data for training and RAG"""
    
    def __init__(self):
        self.processed_data = []
        self.qa_pairs = []
        self.embeddings_data = []
    
    def load_raw_data(self, filename: str = "hardware_data.json") -> Dict:
        """Load raw collected data"""
        filepath = RAW_DATA_DIR / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error(f"Raw data file not found: {filepath}")
            return {}
    
    def process_component_data(self, component_name: str, component_data: Dict) -> List[Dict]:
        """Process data for a single component"""
        processed_items = []
        
        # Basic component information
        config = component_data.get('config', {})
        base_info = {
            'component': component_name,
            'category': config.get('category', ''),
            'pins': config.get('pins', 0),
            'interfaces': config.get('interfaces', []),
            'voltage': config.get('voltage', ''),
            'description': config.get('description', '')
        }
        
        # Process Wokwi data
        wokwi_data = component_data.get('wokwi', {})
        if wokwi_data:
            processed_items.extend(self._process_wokwi_data(base_info, wokwi_data))
        
        # Process Arduino data
        arduino_data = component_data.get('arduino', {})
        if arduino_data:
            processed_items.extend(self._process_arduino_data(base_info, arduino_data))
        
        # Process datasheet data
        datasheet_data = component_data.get('datasheets', {})
        if datasheet_data:
            processed_items.extend(self._process_datasheet_data(base_info, datasheet_data))
        
        return processed_items
    
    def _process_wokwi_data(self, base_info: Dict, wokwi_data: Dict) -> List[Dict]:
        """Process Wokwi-specific data"""
        items = []
        
        # Pin information
        pins = wokwi_data.get('pins', {})
        if pins:
            for pin_name, pin_desc in pins.items():
                items.append({
                    **base_info,
                    'data_type': 'pin_info',
                    'pin_name': pin_name,
                    'pin_description': pin_desc,
                    'text': f"Pin {pin_name} of {base_info['component']}: {pin_desc}",
                    'source': 'wokwi'
                })
        
        # Specifications
        specs = wokwi_data.get('specifications', {})
        if specs:
            for spec_name, spec_value in specs.items():
                items.append({
                    **base_info,
                    'data_type': 'specification',
                    'spec_name': spec_name,
                    'spec_value': spec_value,
                    'text': f"{base_info['component']} {spec_name}: {spec_value}",
                    'source': 'wokwi'
                })
        
        # Code examples
        code_examples = wokwi_data.get('code_examples', [])
        for i, example in enumerate(code_examples):
            items.append({
                **base_info,
                'data_type': 'code_example',
                'example_title': example.get('title', f'Example {i+1}'),
                'code': example.get('code', ''),
                'language': example.get('language', 'unknown'),
                'text': f"Code example for {base_info['component']}: {example.get('title', '')}\n{example.get('code', '')}",
                'source': 'wokwi'
            })
        
        # Connections
        connections = wokwi_data.get('connections', [])
        for connection in connections:
            items.append({
                **base_info,
                'data_type': 'connection',
                'connection_from': connection.get('from', ''),
                'connection_to': connection.get('to', ''),
                'text': f"Connection for {base_info['component']}: {connection.get('from', '')} to {connection.get('to', '')}",
                'source': 'wokwi'
            })
        
        return items
    
    def _process_arduino_data(self, base_info: Dict, arduino_data: Dict) -> List[Dict]:
        """Process Arduino-specific data"""
        items = []
        
        # Libraries
        libraries = arduino_data.get('libraries', [])
        for library in libraries:
            items.append({
                **base_info,
                'data_type': 'library',
                'library_name': library,
                'text': f"Arduino library for {base_info['component']}: {library}",
                'source': 'arduino'
            })
        
        # Functions
        functions = arduino_data.get('functions', [])
        for function in functions:
            items.append({
                **base_info,
                'data_type': 'function',
                'function_name': function,
                'text': f"Arduino function for {base_info['component']}: {function}",
                'source': 'arduino'
            })
        
        # Examples
        examples = arduino_data.get('examples', [])
        for i, example in enumerate(examples):
            items.append({
                **base_info,
                'data_type': 'arduino_example',
                'example_type': example.get('type', 'sketch'),
                'code': example.get('code', ''),
                'text': f"Arduino example for {base_info['component']}:\n{example.get('code', '')}",
                'source': 'arduino'
            })
        
        return items
    
    def _process_datasheet_data(self, base_info: Dict, datasheet_data: Dict) -> List[Dict]:
        """Process datasheet and technical data"""
        items = []
        
        data_list = datasheet_data.get('data', [])
        for data_item in data_list:
            site = data_item.get('site', 'unknown')
            content = data_item.get('content', '')
            
            items.append({
                **base_info,
                'data_type': 'datasheet_info',
                'site': site,
                'content': content,
                'text': f"Technical information for {base_info['component']} from {site}: {content[:500]}",
                'source': 'datasheet'
            })
        
        return items
    
    def generate_qa_pairs(self, processed_data: List[Dict]) -> List[Dict]:
        """Generate question-answer pairs for training"""
        qa_pairs = []
        
        for item in processed_data:
            component = item['component']
            
            # Generate different types of questions based on data type
            if item['data_type'] == 'pin_info':
                questions = [
                    f"What is the {item['pin_name']} pin used for in {component}?",
                    f"Describe the {item['pin_name']} pin of {component}",
                    f"What does pin {item['pin_name']} do in {component}?"
                ]
                answer = item['pin_description']
                
            elif item['data_type'] == 'specification':
                questions = [
                    f"What is the {item['spec_name']} of {component}?",
                    f"Tell me about the {item['spec_name']} specification for {component}",
                    f"What are the {item['spec_name']} specifications for {component}?"
                ]
                answer = item['spec_value']
                
            elif item['data_type'] == 'code_example':
                questions = [
                    f"How do I program {component}?",
                    f"Show me code example for {component}",
                    f"How to use {component} in code?",
                    f"Give me a programming example for {component}"
                ]
                answer = f"Here's an example:\n{item['code']}"
                
            elif item['data_type'] == 'connection':
                questions = [
                    f"How do I wire {component}?",
                    f"What are the connections for {component}?",
                    f"How to connect {component}?",
                    f"Show me the wiring for {component}"
                ]
                answer = f"Connect {item['connection_from']} to {item['connection_to']}"
                
            else:
                # General questions
                questions = [
                    f"Tell me about {component}",
                    f"What is {component}?",
                    f"Describe {component}",
                    f"How does {component} work?"
                ]
                answer = item.get('text', item.get('description', ''))
            
            # Add context to answers
            context_info = f"\nComponent: {component}\nCategory: {item['category']}\nVoltage: {item['voltage']}\nInterfaces: {', '.join(item['interfaces'])}"
            
            for question in questions:
                qa_pairs.append({
                    'question': question,
                    'answer': answer + context_info,
                    'component': component,
                    'category': item['category'],
                    'data_type': item['data_type'],
                    'source': item['source']
                })
        
        return qa_pairs
    
    def create_embeddings_data(self, processed_data: List[Dict]) -> List[Dict]:
        """Create data suitable for embedding and RAG"""
        embeddings_data = []
        
        for item in processed_data:
            # Create comprehensive text for embedding
            text_parts = [
                f"Component: {item['component']}",
                f"Category: {item['category']}",
                f"Description: {item['description']}"
            ]
            
            if item['interfaces']:
                text_parts.append(f"Interfaces: {', '.join(item['interfaces'])}")
            
            if item['voltage']:
                text_parts.append(f"Voltage: {item['voltage']}")
            
            # Add specific data based on type
            if item['data_type'] == 'pin_info':
                text_parts.append(f"Pin {item['pin_name']}: {item['pin_description']}")
            elif item['data_type'] == 'specification':
                text_parts.append(f"{item['spec_name']}: {item['spec_value']}")
            elif item['data_type'] == 'code_example':
                text_parts.append(f"Code example: {item['code'][:200]}...")  # Truncate long code
            
            embeddings_data.append({
                'id': f"{item['component']}_{item['data_type']}_{len(embeddings_data)}",
                'text': '\n'.join(text_parts),
                'metadata': {
                    'component': item['component'],
                    'category': item['category'],
                    'data_type': item['data_type'],
                    'source': item['source'],
                    'interfaces': item['interfaces'],
                    'voltage': item['voltage']
                }
            })
        
        return embeddings_data
    
    def save_processed_data(self, processed_data: List[Dict], qa_pairs: List[Dict], 
                          embeddings_data: List[Dict]):
        """Save all processed data"""
        
        # Save processed data
        with open(PROCESSED_DATA_DIR / "processed_hardware_data.json", 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        # Save QA pairs
        with open(PROCESSED_DATA_DIR / "qa_pairs.json", 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        
        # Save embeddings data
        with open(PROCESSED_DATA_DIR / "embeddings_data.json", 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)
        
        # Create datasets for training
        qa_df = pd.DataFrame(qa_pairs)
        qa_df.to_csv(PROCESSED_DATA_DIR / "qa_pairs.csv", index=False)
        
        embeddings_df = pd.DataFrame(embeddings_data)
        embeddings_df.to_csv(PROCESSED_DATA_DIR / "embeddings_data.csv", index=False)
        
        logger.info(f"Processed data saved:")
        logger.info(f"- {len(processed_data)} processed items")
        logger.info(f"- {len(qa_pairs)} QA pairs")
        logger.info(f"- {len(embeddings_data)} embedding items")
    
    def process_all_data(self, raw_data: Dict) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Process all raw data"""
        all_processed_data = []
        
        for component_name, component_data in raw_data.items():
            logger.info(f"Processing data for {component_name}")
            processed_items = self.process_component_data(component_name, component_data)
            all_processed_data.extend(processed_items)
        
        # Generate QA pairs and embeddings data
        qa_pairs = self.generate_qa_pairs(all_processed_data)
        embeddings_data = self.create_embeddings_data(all_processed_data)
        
        return all_processed_data, qa_pairs, embeddings_data

def main():
    """Main processing function"""
    processor = DataProcessor()
    
    # Load raw data
    raw_data = processor.load_raw_data()
    
    if not raw_data:
        logger.error("No raw data found. Please run data collection first.")
        return
    
    # Process all data
    processed_data, qa_pairs, embeddings_data = processor.process_all_data(raw_data)
    
    # Save processed data
    processor.save_processed_data(processed_data, qa_pairs, embeddings_data)
    
    logger.info("Data processing completed!")

if __name__ == "__main__":
    main()
