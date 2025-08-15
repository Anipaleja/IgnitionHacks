"""
Comprehensive Training Data Processor
Converts comprehensive hardware data into extensive training datasets
for creating an AI model that knows EVERYTHING about hardware components
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
import re
import numpy as np
from datasets import Dataset
import logging
from itertools import combinations
import random

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, HARDWARE_COMPONENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDataProcessor:
    """Process comprehensive hardware data for training an all-knowing AI model"""
    
    def __init__(self):
        self.training_examples = []
        self.knowledge_statements = []
        self.qa_pairs = []
        
        # Question templates for comprehensive knowledge
        self.question_templates = {
            'physical': [
                "What color is the {component}?",
                "What are the physical dimensions of {component}?",
                "What package type is {component}?",
                "How is {component} mounted?",
                "What does {component} look like?",
                "Describe the physical appearance of {component}",
                "What are the color codes on {component}?",
                "What markings are on {component}?",
            ],
            'pins': [
                "What color is pin {pin} on {component}?",
                "What is the function of pin {pin} on {component}?",
                "Which pin on {component} is for {function}?",
                "How are the pins arranged on {component}?",
                "What is the pin spacing on {component}?",
                "Which pins are power pins on {component}?",
                "Which pins are ground pins on {component}?",
                "What voltage level is pin {pin} on {component}?",
                "What is the current rating for pin {pin} on {component}?",
                "Describe all pins on {component}",
            ],
            'electrical': [
                "What is the operating voltage of {component}?",
                "What is the maximum voltage for {component}?",
                "What is the current consumption of {component}?",
                "What is the power consumption of {component}?",
                "What are the electrical specifications of {component}?",
                "What is the input impedance of {component}?",
                "What is the output impedance of {component}?",
                "What frequency does {component} operate at?",
                "What are the timing characteristics of {component}?",
            ],
            'wiring': [
                "How do I wire {component} to {target}?",
                "What connections are needed for {component}?",
                "How do I connect {component} step by step?",
                "What wires do I need for {component}?",
                "Show me the wiring diagram for {component}",
                "What are common wiring mistakes with {component}?",
                "How do I breadboard {component}?",
                "What resistors are needed with {component}?",
                "How do I solder {component}?",
            ],
            'programming': [
                "What library do I need for {component}?",
                "How do I initialize {component} in code?",
                "Show me example code for {component}",
                "What functions are available for {component}?",
                "How do I read data from {component}?",
                "How do I write data to {component}?",
                "What are the advanced features of {component}?",
                "How do I configure {component}?",
            ],
            'troubleshooting': [
                "Why is my {component} not working?",
                "How do I test {component}?",
                "What are common problems with {component}?",
                "How do I debug {component}?",
                "My {component} is giving wrong readings, why?",
                "How do I know if {component} is damaged?",
                "What should I check if {component} doesn't respond?",
                "How do I fix {component} connection issues?",
            ],
            'compatibility': [
                "Can I use {component} with {board}?",
                "Is {component} compatible with 3.3V?",
                "Is {component} compatible with 5V?",
                "What microcontrollers work with {component}?",
                "Can I use {component} with Arduino?",
                "Can I use {component} with ESP32?",
                "What voltage level shifters do I need for {component}?",
            ],
            'performance': [
                "What is the accuracy of {component}?",
                "What is the precision of {component}?",
                "How fast can {component} respond?",
                "What is the bandwidth of {component}?",
                "What is the resolution of {component}?",
                "What is the range of {component}?",
                "How reliable is {component}?",
            ],
            'environmental': [
                "What temperature range can {component} operate in?",
                "What humidity can {component} handle?",
                "Is {component} waterproof?",
                "What environmental protection does {component} have?",
                "Can {component} work outdoors?",
                "What certifications does {component} have?",
            ],
            'alternatives': [
                "What are alternatives to {component}?",
                "What is equivalent to {component}?",
                "What can I use instead of {component}?",
                "What are similar components to {component}?",
                "What is the difference between {component} and {alternative}?",
            ]
        }
    
    def load_comprehensive_data(self) -> List[Dict]:
        """Load comprehensive hardware data"""
        
        # Try to load master file first
        master_file = RAW_DATA_DIR / "comprehensive_hardware_data.json"
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Otherwise, load individual component files
        all_data = []
        for component in HARDWARE_COMPONENTS:
            filename = f"comprehensive_{component['name'].replace(' ', '_').replace('(', '').replace(')', '')}.json"
            filepath = RAW_DATA_DIR / filename
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    comp_data = json.load(f)
                    all_data.append(comp_data)
            else:
                logger.warning(f"No comprehensive data found for {component['name']}")
        
        return all_data
    
    def generate_comprehensive_training_data(self, comprehensive_data: List[Dict]) -> List[Dict]:
        """Generate comprehensive training examples covering all aspects"""
        
        training_examples = []
        
        for comp_data in comprehensive_data:
            component_name = comp_data['name']
            logger.info(f"Generating comprehensive training data for {component_name}")
            
            # Physical characteristics training
            training_examples.extend(self._generate_physical_training(comp_data))
            
            # Pin-specific training (detailed)
            training_examples.extend(self._generate_pin_training(comp_data))
            
            # Electrical specifications training
            training_examples.extend(self._generate_electrical_training(comp_data))
            
            # Wiring and connections training
            training_examples.extend(self._generate_wiring_training(comp_data))
            
            # Programming and code training
            training_examples.extend(self._generate_programming_training(comp_data))
            
            # Troubleshooting training
            training_examples.extend(self._generate_troubleshooting_training(comp_data))
            
            # Compatibility training
            training_examples.extend(self._generate_compatibility_training(comp_data))
            
            # Performance characteristics training
            training_examples.extend(self._generate_performance_training(comp_data))
            
            # Environmental conditions training
            training_examples.extend(self._generate_environmental_training(comp_data))
            
            # Alternative components training
            training_examples.extend(self._generate_alternatives_training(comp_data))
            
            # Cross-component knowledge training
            training_examples.extend(self._generate_cross_component_training(comp_data, comprehensive_data))
        
        logger.info(f"Generated {len(training_examples)} comprehensive training examples")
        return training_examples
    
    def _generate_physical_training(self, comp_data: Dict) -> List[Dict]:
        """Generate training data for physical characteristics"""
        examples = []
        component_name = comp_data['name']
        
        # Physical description
        if comp_data.get('physical_description'):
            for template in self.question_templates['physical']:
                if 'color' in template.lower():
                    if comp_data.get('color_scheme'):
                        examples.append({
                            'question': template.format(component=component_name),
                            'answer': f"The {component_name} has the following colors: " + 
                                    ", ".join([f"{part}: {color}" for part, color in comp_data['color_scheme'].items()]),
                            'context': f"Physical characteristics of {component_name}",
                            'category': 'physical',
                            'component': component_name
                        })
                elif 'dimensions' in template.lower():
                    if comp_data.get('dimensions'):
                        examples.append({
                            'question': template.format(component=component_name),
                            'answer': f"The {component_name} dimensions are: " + 
                                    ", ".join([f"{dim}: {value}" for dim, value in comp_data['dimensions'].items()]),
                            'context': f"Physical specifications of {component_name}",
                            'category': 'physical',
                            'component': component_name
                        })
                elif 'package' in template.lower():
                    if comp_data.get('package_type'):
                        examples.append({
                            'question': template.format(component=component_name),
                            'answer': f"The {component_name} comes in a {comp_data['package_type']} package.",
                            'context': f"Package information for {component_name}",
                            'category': 'physical',
                            'component': component_name
                        })
                elif 'appearance' in template.lower() or 'look' in template.lower():
                    examples.append({
                        'question': template.format(component=component_name),
                        'answer': comp_data['physical_description'],
                        'context': f"Physical appearance of {component_name}",
                        'category': 'physical',
                        'component': component_name
                    })
        
        return examples
    
    def _generate_pin_training(self, comp_data: Dict) -> List[Dict]:
        """Generate detailed pin-specific training data"""
        examples = []
        component_name = comp_data['name']
        
        pin_functions = comp_data.get('pin_functions', {})
        pin_colors = comp_data.get('pin_colors', {})
        
        # Individual pin training
        for pin_name, pin_info in pin_functions.items():
            # Pin function questions
            examples.append({
                'question': f"What is the function of pin {pin_name} on {component_name}?",
                'answer': f"Pin {pin_name} on {component_name} is used for: {pin_info.get('function', 'Not specified')}",
                'context': f"Pin functions of {component_name}",
                'category': 'pins',
                'component': component_name,
                'pin': pin_name
            })
            
            # Pin color questions (if available)
            if pin_name in pin_colors:
                examples.append({
                    'question': f"What color is pin {pin_name} on {component_name}?",
                    'answer': f"Pin {pin_name} on {component_name} is {pin_colors[pin_name]} colored.",
                    'context': f"Pin colors of {component_name}",
                    'category': 'pins',
                    'component': component_name,
                    'pin': pin_name
                })
            
            # Pin voltage/current specifications
            if isinstance(pin_info, dict):
                if 'voltage' in pin_info:
                    examples.append({
                        'question': f"What voltage level is pin {pin_name} on {component_name}?",
                        'answer': f"Pin {pin_name} on {component_name} operates at {pin_info['voltage']}.",
                        'context': f"Pin electrical specifications of {component_name}",
                        'category': 'pins',
                        'component': component_name,
                        'pin': pin_name
                    })
                
                if 'current' in pin_info:
                    examples.append({
                        'question': f"What is the current rating for pin {pin_name} on {component_name}?",
                        'answer': f"Pin {pin_name} on {component_name} can handle {pin_info['current']}.",
                        'context': f"Pin current specifications of {component_name}",
                        'category': 'pins',
                        'component': component_name,
                        'pin': pin_name
                    })
        
        # General pin layout questions
        if comp_data.get('pin_layout'):
            examples.append({
                'question': f"How are the pins arranged on {component_name}?",
                'answer': f"The pins on {component_name} are arranged as follows: {comp_data['pin_layout']}",
                'context': f"Pin layout of {component_name}",
                'category': 'pins',
                'component': component_name
            })
        
        # Pin spacing and physical characteristics
        if comp_data.get('pin_dimensions'):
            for dim_type, value in comp_data['pin_dimensions'].items():
                examples.append({
                    'question': f"What is the pin {dim_type} on {component_name}?",
                    'answer': f"The pin {dim_type} on {component_name} is {value}.",
                    'context': f"Pin physical dimensions of {component_name}",
                    'category': 'pins',
                    'component': component_name
                })
        
        return examples
    
    def _generate_electrical_training(self, comp_data: Dict) -> List[Dict]:
        """Generate electrical specifications training data"""
        examples = []
        component_name = comp_data['name']
        
        # Voltage specifications
        voltage_specs = comp_data.get('voltage_specs', {})
        for spec_type, value in voltage_specs.items():
            examples.append({
                'question': f"What is the {spec_type} voltage of {component_name}?",
                'answer': f"The {spec_type} voltage of {component_name} is {value}.",
                'context': f"Voltage specifications of {component_name}",
                'category': 'electrical',
                'component': component_name
            })
        
        # Current specifications
        current_specs = comp_data.get('current_specs', {})
        for spec_type, value in current_specs.items():
            examples.append({
                'question': f"What is the {spec_type} current of {component_name}?",
                'answer': f"The {spec_type} current of {component_name} is {value}.",
                'context': f"Current specifications of {component_name}",
                'category': 'electrical',
                'component': component_name
            })
        
        # Power consumption
        power_specs = comp_data.get('power_consumption', {})
        for power_type, value in power_specs.items():
            examples.append({
                'question': f"What is the {power_type} power consumption of {component_name}?",
                'answer': f"The {power_type} power consumption of {component_name} is {value}.",
                'context': f"Power specifications of {component_name}",
                'category': 'electrical',
                'component': component_name
            })
        
        # Frequency specifications
        freq_specs = comp_data.get('frequency_specs', {})
        for freq_type, value in freq_specs.items():
            examples.append({
                'question': f"What {freq_type} frequency does {component_name} operate at?",
                'answer': f"The {component_name} operates at {value} for {freq_type}.",
                'context': f"Frequency specifications of {component_name}",
                'category': 'electrical',
                'component': component_name
            })
        
        return examples
    
    def _generate_wiring_training(self, comp_data: Dict) -> List[Dict]:
        """Generate comprehensive wiring and connection training data"""
        examples = []
        component_name = comp_data['name']
        
        # Typical connections
        typical_connections = comp_data.get('typical_connections', [])
        for connection in typical_connections:
            if isinstance(connection, dict):
                target = connection.get('target', 'microcontroller')
                steps = connection.get('steps', [])
                
                examples.append({
                    'question': f"How do I wire {component_name} to {target}?",
                    'answer': f"To wire {component_name} to {target}: " + 
                             ". ".join(steps) if steps else f"Connect {component_name} according to the pinout.",
                    'context': f"Wiring instructions for {component_name}",
                    'category': 'wiring',
                    'component': component_name
                })
        
        # Connection examples
        connection_examples = comp_data.get('connection_examples', [])
        for example in connection_examples:
            if isinstance(example, dict):
                examples.append({
                    'question': f"Show me a step-by-step connection for {component_name}",
                    'answer': example.get('description', 'Connection example available'),
                    'context': f"Connection examples for {component_name}",
                    'category': 'wiring',
                    'component': component_name
                })
        
        # Common wiring mistakes
        common_mistakes = comp_data.get('common_mistakes', [])
        if common_mistakes:
            examples.append({
                'question': f"What are common wiring mistakes with {component_name}?",
                'answer': f"Common wiring mistakes with {component_name}: " + "; ".join(common_mistakes),
                'context': f"Wiring troubleshooting for {component_name}",
                'category': 'wiring',
                'component': component_name
            })
        
        return examples
    
    def _generate_programming_training(self, comp_data: Dict) -> List[Dict]:
        """Generate programming and code training data"""
        examples = []
        component_name = comp_data['name']
        
        # Required libraries
        required_libraries = comp_data.get('required_libraries', [])
        for library in required_libraries:
            if isinstance(library, dict):
                lib_name = library.get('name', library.get('library', ''))
                purpose = library.get('purpose', 'component control')
                
                examples.append({
                    'question': f"What library do I need for {component_name}?",
                    'answer': f"For {component_name}, you need the {lib_name} library. It is used for {purpose}.",
                    'context': f"Programming libraries for {component_name}",
                    'category': 'programming',
                    'component': component_name
                })
        
        # Initialization code
        initialization_code = comp_data.get('initialization_code', [])
        for init_code in initialization_code:
            if isinstance(init_code, dict):
                language = init_code.get('language', 'Arduino')
                code = init_code.get('code', '')
                
                examples.append({
                    'question': f"How do I initialize {component_name} in {language}?",
                    'answer': f"To initialize {component_name} in {language}:\n{code}",
                    'context': f"Initialization code for {component_name}",
                    'category': 'programming',
                    'component': component_name
                })
        
        # Example functions
        example_functions = comp_data.get('example_functions', [])
        for function in example_functions:
            if isinstance(function, dict):
                func_name = function.get('function', function.get('name', ''))
                usage = function.get('usage', function.get('description', ''))
                
                examples.append({
                    'question': f"How do I use the {func_name} function with {component_name}?",
                    'answer': f"The {func_name} function for {component_name}: {usage}",
                    'context': f"Function usage for {component_name}",
                    'category': 'programming',
                    'component': component_name
                })
        
        return examples
    
    def _generate_troubleshooting_training(self, comp_data: Dict) -> List[Dict]:
        """Generate troubleshooting and debugging training data"""
        examples = []
        component_name = comp_data['name']
        
        # Common issues
        common_issues = comp_data.get('common_issues', [])
        for issue in common_issues:
            if isinstance(issue, dict):
                problem = issue.get('problem', '')
                solution = issue.get('solution', '')
                
                examples.append({
                    'question': f"Why is my {component_name} {problem}?",
                    'answer': f"If your {component_name} is {problem}, try this: {solution}",
                    'context': f"Troubleshooting {component_name}",
                    'category': 'troubleshooting',
                    'component': component_name
                })
            elif isinstance(issue, str):
                examples.append({
                    'question': f"What problems can occur with {component_name}?",
                    'answer': f"A common problem with {component_name} is: {issue}",
                    'context': f"Common issues with {component_name}",
                    'category': 'troubleshooting',
                    'component': component_name
                })
        
        # Debugging tips
        debugging_tips = comp_data.get('debugging_tips', [])
        if debugging_tips:
            examples.append({
                'question': f"How do I debug {component_name}?",
                'answer': f"To debug {component_name}: " + "; ".join(debugging_tips),
                'context': f"Debugging tips for {component_name}",
                'category': 'troubleshooting',
                'component': component_name
            })
        
        # Testing procedures
        testing_procedures = comp_data.get('testing_procedures', [])
        for test in testing_procedures:
            if isinstance(test, dict):
                test_name = test.get('test', 'functionality test')
                expected = test.get('expected_result', 'proper operation')
                
                examples.append({
                    'question': f"How do I test {component_name}?",
                    'answer': f"To test {component_name}, perform a {test_name}. You should see {expected}.",
                    'context': f"Testing procedures for {component_name}",
                    'category': 'troubleshooting',
                    'component': component_name
                })
        
        return examples
    
    def _generate_compatibility_training(self, comp_data: Dict) -> List[Dict]:
        """Generate compatibility training data"""
        examples = []
        component_name = comp_data['name']
        
        # Compatible boards
        compatible_boards = comp_data.get('compatible_boards', [])
        for board in compatible_boards:
            examples.append({
                'question': f"Can I use {component_name} with {board}?",
                'answer': f"Yes, {component_name} is compatible with {board}.",
                'context': f"Board compatibility for {component_name}",
                'category': 'compatibility',
                'component': component_name
            })
        
        # Voltage level compatibility
        voltage_compatibility = comp_data.get('voltage_level_compatibility', {})
        for voltage, boards in voltage_compatibility.items():
            for board in boards:
                examples.append({
                    'question': f"Is {component_name} compatible with {voltage} systems?",
                    'answer': f"Yes, {component_name} works with {voltage} systems like {board}.",
                    'context': f"Voltage compatibility for {component_name}",
                    'category': 'compatibility',
                    'component': component_name
                })
        
        return examples
    
    def _generate_performance_training(self, comp_data: Dict) -> List[Dict]:
        """Generate performance characteristics training data"""
        examples = []
        component_name = comp_data['name']
        
        # Accuracy and precision
        accuracy_precision = comp_data.get('accuracy_precision', {})
        for metric, value in accuracy_precision.items():
            examples.append({
                'question': f"What is the {metric} of {component_name}?",
                'answer': f"The {metric} of {component_name} is {value}.",
                'context': f"Performance specifications of {component_name}",
                'category': 'performance',
                'component': component_name
            })
        
        # Response time
        response_time = comp_data.get('response_time', {})
        for timing_type, value in response_time.items():
            examples.append({
                'question': f"How fast is the {timing_type} of {component_name}?",
                'answer': f"The {timing_type} of {component_name} is {value}.",
                'context': f"Timing characteristics of {component_name}",
                'category': 'performance',
                'component': component_name
            })
        
        return examples
    
    def _generate_environmental_training(self, comp_data: Dict) -> List[Dict]:
        """Generate environmental conditions training data"""
        examples = []
        component_name = comp_data['name']
        
        # Temperature range
        temperature_range = comp_data.get('temperature_range', {})
        for temp_type, value in temperature_range.items():
            examples.append({
                'question': f"What {temp_type} temperature can {component_name} handle?",
                'answer': f"The {temp_type} temperature range for {component_name} is {value}.",
                'context': f"Environmental specifications of {component_name}",
                'category': 'environmental',
                'component': component_name
            })
        
        # Humidity range
        humidity_range = comp_data.get('humidity_range', '')
        if humidity_range:
            examples.append({
                'question': f"What humidity can {component_name} handle?",
                'answer': f"{component_name} can operate in humidity levels of {humidity_range}.",
                'context': f"Environmental specifications of {component_name}",
                'category': 'environmental',
                'component': component_name
            })
        
        # Environmental protection
        env_protection = comp_data.get('environmental_protection', '')
        if env_protection:
            examples.append({
                'question': f"What environmental protection does {component_name} have?",
                'answer': f"{component_name} has {env_protection} environmental protection.",
                'context': f"Environmental protection of {component_name}",
                'category': 'environmental',
                'component': component_name
            })
        
        return examples
    
    def _generate_alternatives_training(self, comp_data: Dict) -> List[Dict]:
        """Generate alternative components training data"""
        examples = []
        component_name = comp_data['name']
        
        # Alternative parts
        alternative_parts = comp_data.get('alternative_parts', [])
        if alternative_parts:
            examples.append({
                'question': f"What are alternatives to {component_name}?",
                'answer': f"Alternatives to {component_name} include: " + ", ".join(alternative_parts),
                'context': f"Alternative components to {component_name}",
                'category': 'alternatives',
                'component': component_name
            })
            
            # Individual alternative comparisons
            for alt in alternative_parts:
                examples.append({
                    'question': f"What is the difference between {component_name} and {alt}?",
                    'answer': f"{component_name} and {alt} are similar components with different specifications and features.",
                    'context': f"Component comparison: {component_name} vs {alt}",
                    'category': 'alternatives',
                    'component': component_name
                })
        
        return examples
    
    def _generate_cross_component_training(self, comp_data: Dict, all_data: List[Dict]) -> List[Dict]:
        """Generate training data involving multiple components"""
        examples = []
        component_name = comp_data['name']
        
        # Generate questions about using this component with others
        other_components = [d['name'] for d in all_data if d['name'] != component_name]
        
        for other_comp in other_components[:5]:  # Limit to avoid explosion
            # Compatibility questions
            examples.append({
                'question': f"Can I use {component_name} together with {other_comp}?",
                'answer': f"Yes, {component_name} can typically be used with {other_comp} in the same project, "
                         f"as long as you have enough pins and power supply capacity.",
                'context': f"Multi-component usage: {component_name} and {other_comp}",
                'category': 'integration',
                'component': component_name
            })
            
            # Project-based questions
            examples.append({
                'question': f"How do I make a project with {component_name} and {other_comp}?",
                'answer': f"To create a project with {component_name} and {other_comp}, "
                         f"first connect each component according to their individual wiring requirements, "
                         f"then write code to handle both components.",
                'context': f"Project integration: {component_name} and {other_comp}",
                'category': 'integration',
                'component': component_name
            })
        
        return examples
    
    def create_specialized_datasets(self, training_examples: List[Dict]) -> Dict[str, List[Dict]]:
        """Create specialized datasets for different types of knowledge"""
        
        specialized_datasets = {
            'physical_knowledge': [],
            'electrical_knowledge': [],
            'programming_knowledge': [],
            'wiring_knowledge': [],
            'troubleshooting_knowledge': [],
            'compatibility_knowledge': [],
            'performance_knowledge': [],
            'environmental_knowledge': [],
            'integration_knowledge': []
        }
        
        for example in training_examples:
            category = example.get('category', 'general')
            
            if category in ['physical']:
                specialized_datasets['physical_knowledge'].append(example)
            elif category in ['electrical', 'pins']:
                specialized_datasets['electrical_knowledge'].append(example)
            elif category in ['programming']:
                specialized_datasets['programming_knowledge'].append(example)
            elif category in ['wiring']:
                specialized_datasets['wiring_knowledge'].append(example)
            elif category in ['troubleshooting']:
                specialized_datasets['troubleshooting_knowledge'].append(example)
            elif category in ['compatibility']:
                specialized_datasets['compatibility_knowledge'].append(example)
            elif category in ['performance']:
                specialized_datasets['performance_knowledge'].append(example)
            elif category in ['environmental']:
                specialized_datasets['environmental_knowledge'].append(example)
            elif category in ['integration']:
                specialized_datasets['integration_knowledge'].append(example)
        
        return specialized_datasets
    
    def augment_training_data(self, examples: List[Dict]) -> List[Dict]:
        """Augment training data with variations and additional context"""
        
        augmented_examples = []
        
        for example in examples:
            # Original example
            augmented_examples.append(example)
            
            # Generate variations
            question = example['question']
            answer = example['answer']
            component = example['component']
            
            # Question variations
            variations = [
                question.replace("What is", "Tell me about"),
                question.replace("How do I", "How can I"),
                question.replace("Show me", "Give me"),
                question.replace("?", " please?"),
            ]
            
            for variation in variations:
                if variation != question:
                    augmented_examples.append({
                        **example,
                        'question': variation,
                        'augmented': True
                    })
            
            # Add context-rich versions
            rich_context = f"In the context of electronics and hardware projects, {answer}"
            augmented_examples.append({
                **example,
                'answer': rich_context,
                'context_enriched': True
            })
        
        return augmented_examples
    
    def save_comprehensive_training_data(self, training_examples: List[Dict], 
                                       specialized_datasets: Dict[str, List[Dict]]):
        """Save all comprehensive training data"""
        
        # Save main training dataset
        with open(PROCESSED_DATA_DIR / "comprehensive_training_data.json", 'w', encoding='utf-8') as f:
            json.dump(training_examples, f, indent=2, ensure_ascii=False)
        
        # Save as CSV for easy viewing
        df = pd.DataFrame(training_examples)
        df.to_csv(PROCESSED_DATA_DIR / "comprehensive_training_data.csv", index=False)
        
        # Save specialized datasets
        for dataset_name, dataset in specialized_datasets.items():
            filename = f"{dataset_name}_training.json"
            with open(PROCESSED_DATA_DIR / filename, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        # Create summary statistics
        stats = {
            'total_examples': len(training_examples),
            'examples_by_category': {},
            'examples_by_component': {},
            'specialized_datasets': {name: len(data) for name, data in specialized_datasets.items()}
        }
        
        for example in training_examples:
            category = example.get('category', 'unknown')
            component = example.get('component', 'unknown')
            
            stats['examples_by_category'][category] = stats['examples_by_category'].get(category, 0) + 1
            stats['examples_by_component'][component] = stats['examples_by_component'].get(component, 0) + 1
        
        with open(PROCESSED_DATA_DIR / "training_data_stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved comprehensive training data:")
        logger.info(f"   Total examples: {stats['total_examples']}")
        logger.info(f"   Categories: {len(stats['examples_by_category'])}")
        logger.info(f"   Components: {len(stats['examples_by_component'])}")
        logger.info(f"   Specialized datasets: {len(specialized_datasets)}")

def main():
    """Main comprehensive data processing function"""
    logger.info("Starting comprehensive training data processing...")
    
    processor = ComprehensiveDataProcessor()
    
    # Load comprehensive data
    comprehensive_data = processor.load_comprehensive_data()
    
    if not comprehensive_data:
        logger.error("No comprehensive data found. Please run comprehensive data collection first.")
        return
    
    logger.info(f"Loaded data for {len(comprehensive_data)} components")
    
    # Generate comprehensive training data
    training_examples = processor.generate_comprehensive_training_data(comprehensive_data)
    
    # Augment training data
    logger.info("Augmenting training data...")
    augmented_examples = processor.augment_training_data(training_examples)
    
    # Create specialized datasets
    logger.info("Creating specialized datasets...")
    specialized_datasets = processor.create_specialized_datasets(augmented_examples)
    
    # Save all data
    processor.save_comprehensive_training_data(augmented_examples, specialized_datasets)
    
    logger.info("Comprehensive training data processing completed!")

if __name__ == "__main__":
    main()
