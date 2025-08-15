"""
Main application interface for the AI Hardware Understanding System
"""

import gradio as gr
import json
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from vector_database import VectorDatabase, RAGSystem, load_and_index_data
from model_trainer import HardwareModelTrainer
from config import HARDWARE_COMPONENTS, MODELS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardwareAssistant:
    """Main AI Hardware Assistant"""
    
    def __init__(self):
        self.vector_db = None
        self.rag_system = None
        self.fine_tuned_model = None
        self.trainer = None
        self.initialize_systems()
    
    def initialize_systems(self):
        """Initialize all AI systems"""
        try:
            # Initialize vector database and RAG
            self.vector_db = load_and_index_data()
            if self.vector_db:
                self.rag_system = RAGSystem(self.vector_db)
                logger.info("RAG system initialized successfully")
            
            # Try to load fine-tuned model
            model_path = MODELS_DIR / "hardware_model"
            if model_path.exists():
                self.trainer = HardwareModelTrainer()
                self.trainer.load_trained_model(str(model_path))
                logger.info("Fine-tuned model loaded successfully")
            else:
                logger.info("No fine-tuned model found. Using RAG only.")
                
        except Exception as e:
            logger.error(f"Error initializing systems: {e}")
    
    def get_component_list(self) -> List[str]:
        """Get list of available components"""
        return [comp['name'] for comp in HARDWARE_COMPONENTS]
    
    def get_component_categories(self) -> List[str]:
        """Get list of component categories"""
        categories = set([comp['category'] for comp in HARDWARE_COMPONENTS])
        return list(categories)
    
    def answer_question(self, question: str, component: str = None, 
                       category: str = None, use_fine_tuned: bool = True) -> Dict[str, Any]:
        """Answer hardware-related questions"""
        
        response_data = {
            'question': question,
            'rag_response': '',
            'fine_tuned_response': '',
            'context': '',
            'component': component,
            'category': category
        }
        
        # Get RAG response
        if self.rag_system:
            try:
                rag_result = self.rag_system.answer_question(question, component, category)
                response_data['rag_response'] = rag_result['response']
                response_data['context'] = rag_result['context']
            except Exception as e:
                logger.error(f"RAG error: {e}")
                response_data['rag_response'] = "Error generating RAG response"
        
        # Get fine-tuned model response
        if use_fine_tuned and self.trainer and self.trainer.model:
            try:
                results = self.trainer.evaluate_model([question])
                if results:
                    response_data['fine_tuned_response'] = results[0]['response']
            except Exception as e:
                logger.error(f"Fine-tuned model error: {e}")
                response_data['fine_tuned_response'] = "Error generating fine-tuned response"
        
        return response_data
    
    def get_component_info(self, component_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a component"""
        
        if not self.vector_db:
            return {'error': 'Vector database not initialized'}
        
        try:
            # Get all information about the component
            results = self.vector_db.get_component_info(component_name)
            
            # Organize by data type
            organized_info = {
                'component': component_name,
                'pins': [],
                'specifications': [],
                'code_examples': [],
                'connections': [],
                'general_info': []
            }
            
            for result in results:
                data_type = result['metadata'].get('data_type', 'general_info')
                if data_type == 'pin_info':
                    organized_info['pins'].append(result['text'])
                elif data_type == 'specification':
                    organized_info['specifications'].append(result['text'])
                elif data_type in ['code_example', 'arduino_example']:
                    organized_info['code_examples'].append(result['text'])
                elif data_type == 'connection':
                    organized_info['connections'].append(result['text'])
                else:
                    organized_info['general_info'].append(result['text'])
            
            return organized_info
            
        except Exception as e:
            logger.error(f"Error getting component info: {e}")
            return {'error': str(e)}
    
    def search_components(self, query: str, category: str = None) -> List[Dict]:
        """Search for components based on query"""
        
        if not self.vector_db:
            return []
        
        try:
            if category and category != "All":
                results = self.vector_db.search_by_category(category, query)
            else:
                results = self.vector_db.search(query)
            
            # Extract unique components from results
            components = {}
            for result in results:
                comp_name = result['metadata']['component']
                if comp_name not in components:
                    components[comp_name] = {
                        'name': comp_name,
                        'category': result['metadata']['category'],
                        'relevance': 1 - result['distance'],  # Convert distance to relevance
                        'snippet': result['text'][:200] + "..."
                    }
            
            return list(components.values())
            
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get vector database statistics"""
        
        if not self.vector_db:
            return {'error': 'Vector database not initialized'}
        
        try:
            return self.vector_db.get_database_stats()
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'error': str(e)}

def create_gradio_interface():
    """Create Gradio interface for the Hardware Assistant"""
    
    assistant = HardwareAssistant()
    
    def process_question(question, component, category, use_fine_tuned):
        """Process question and return formatted response"""
        
        if not question.strip():
            return "Please enter a question."
        
        # Clean inputs
        component = component if component != "All" else None
        category = category if category != "All" else None
        
        # Get response
        result = assistant.answer_question(question, component, category, use_fine_tuned)
        
        # Format response
        response_parts = []
        
        if result['rag_response']:
            response_parts.append(f"**RAG Response:**\n{result['rag_response']}")
        
        if result['fine_tuned_response']:
            response_parts.append(f"**Fine-tuned Model Response:**\n{result['fine_tuned_response']}")
        
        if not response_parts:
            response_parts.append("No response generated. Please check if the system is properly initialized.")
        
        return "\n\n---\n\n".join(response_parts)
    
    def show_component_info(component_name):
        """Show detailed component information"""
        
        if component_name == "All":
            return "Please select a specific component."
        
        info = assistant.get_component_info(component_name)
        
        if 'error' in info:
            return f"Error: {info['error']}"
        
        # Format component information
        sections = []
        
        if info['pins']:
            sections.append(f"**Pins:**\n" + "\n".join(info['pins']))
        
        if info['specifications']:
            sections.append(f"**Specifications:**\n" + "\n".join(info['specifications']))
        
        if info['connections']:
            sections.append(f"**Connections:**\n" + "\n".join(info['connections']))
        
        if info['code_examples']:
            sections.append(f"**Code Examples:**\n" + "\n".join(info['code_examples'][:2]))  # Limit examples
        
        if info['general_info']:
            sections.append(f"**General Information:**\n" + "\n".join(info['general_info'][:3]))
        
        if not sections:
            return f"No detailed information found for {component_name}"
        
        return f"# {component_name}\n\n" + "\n\n".join(sections)
    
    def search_hardware(query, category):
        """Search for hardware components"""
        
        if not query.strip():
            return "Please enter a search query."
        
        results = assistant.search_components(query, category)
        
        if not results:
            return "No components found matching your search."
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(
                f"**{result['name']}** ({result['category']})\n"
                f"Relevance: {result['relevance']:.2f}\n"
                f"{result['snippet']}"
            )
        
        return "\n\n---\n\n".join(formatted_results[:5])  # Show top 5 results
    
    def show_stats():
        """Show database statistics"""
        stats = assistant.get_database_stats()
        
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        # Format stats
        output = f"**Database Statistics:**\n\n"
        output += f"Total Documents: {stats['total_documents']}\n\n"
        
        output += f"**Components ({len(stats['components'])}):**\n"
        for comp, count in sorted(stats['components'].items()):
            output += f"- {comp}: {count} documents\n"
        
        output += f"\n**Categories ({len(stats['categories'])}):**\n"
        for cat, count in sorted(stats['categories'].items()):
            output += f"- {cat}: {count} documents\n"
        
        output += f"\n**Data Types ({len(stats['data_types'])}):**\n"
        for dtype, count in sorted(stats['data_types'].items()):
            output += f"- {dtype}: {count} documents\n"
        
        return output
    
    # Get component and category lists
    components = ["All"] + assistant.get_component_list()
    categories = ["All"] + assistant.get_component_categories()
    
    # Create Gradio interface
    with gr.Blocks(title="AI Hardware Understanding System", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("# AI Hardware Understanding System")
        gr.Markdown("Ask questions about hardware components, get pin information, wiring diagrams, and code examples!")
        
        with gr.Tabs():
            
            # Q&A Tab
            with gr.TabItem("Ask Questions"):
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Your Question",
                            placeholder="e.g., How do I connect ESP32 to DHT22 sensor?",
                            lines=2
                        )
                        with gr.Row():
                            component_filter = gr.Dropdown(
                                choices=components,
                                value="All",
                                label="Filter by Component"
                            )
                            category_filter = gr.Dropdown(
                                choices=categories,
                                value="All",
                                label="Filter by Category"
                            )
                        use_fine_tuned = gr.Checkbox(
                            label="Use Fine-tuned Model (if available)",
                            value=True
                        )
                        ask_button = gr.Button("Ask Question", variant="primary")
                    
                    with gr.Column(scale=3):
                        answer_output = gr.Markdown(label="Answer")
                
                ask_button.click(
                    process_question,
                    inputs=[question_input, component_filter, category_filter, use_fine_tuned],
                    outputs=answer_output
                )
            
            # Component Info Tab
            with gr.TabItem("Component Information"):
                with gr.Row():
                    with gr.Column(scale=1):
                        component_select = gr.Dropdown(
                            choices=components,
                            value="ESP32",
                            label="Select Component"
                        )
                        info_button = gr.Button("Get Information", variant="primary")
                    
                    with gr.Column(scale=3):
                        component_info_output = gr.Markdown(label="Component Details")
                
                info_button.click(
                    show_component_info,
                    inputs=component_select,
                    outputs=component_info_output
                )
            
            # Search Tab
            with gr.TabItem("Search Components"):
                with gr.Row():
                    with gr.Column(scale=2):
                        search_input = gr.Textbox(
                            label="Search Query",
                            placeholder="e.g., temperature sensor, bluetooth module",
                            lines=1
                        )
                        search_category = gr.Dropdown(
                            choices=categories,
                            value="All",
                            label="Filter by Category"
                        )
                        search_button = gr.Button("Search", variant="primary")
                    
                    with gr.Column(scale=3):
                        search_output = gr.Markdown(label="Search Results")
                
                search_button.click(
                    search_hardware,
                    inputs=[search_input, search_category],
                    outputs=search_output
                )
            
            # Statistics Tab
            with gr.TabItem("Database Statistics"):
                with gr.Column():
                    stats_button = gr.Button("Refresh Statistics", variant="primary")
                    stats_output = gr.Markdown(label="Statistics")
                
                stats_button.click(show_stats, outputs=stats_output)
                
                # Load stats on startup
                demo.load(show_stats, outputs=stats_output)
        
        # Example questions
        gr.Markdown("### Example Questions:")
        examples = [
            "What pins does ESP32 have and what are they used for?",
            "How do I connect DHT22 sensor to Arduino Uno?",
            "Show me code example for reading MPU6050 data",
            "What is the voltage requirement for HC-SR04 ultrasonic sensor?",
            "How to wire WS2812 RGB LED strip?",
            "What I2C address does SSD1306 OLED display use?",
            "How to control servo motor with Arduino?",
            "What are the specifications of BMP280 sensor?"
        ]
        
        for example in examples:
            gr.Markdown(f"- {example}")
    
    return demo

def main():
    """Main application entry point"""
    
    # Create and launch Gradio interface
    demo = create_gradio_interface()
    
    # Launch with public sharing for demo purposes
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public sharing
        debug=True
    )

if __name__ == "__main__":
    main()
