"""
Vector database and RAG implementation using ChromaDB
"""

import chromadb
from chromadb.config import Settings
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from pathlib import Path

from config import VECTOR_DB_DIR, VECTOR_DB_CONFIG, PROCESSED_DATA_DIR, MODEL_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabase:
    """Manages vector database for RAG"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or str(VECTOR_DB_DIR)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(MODEL_CONFIG['embedding_model'])
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(
                name=VECTOR_DB_CONFIG['collection_name']
            )
            logger.info(f"Using existing collection: {VECTOR_DB_CONFIG['collection_name']}")
        except:
            collection = self.client.create_collection(
                name=VECTOR_DB_CONFIG['collection_name'],
                metadata={"description": "Hardware components knowledge base"}
            )
            logger.info(f"Created new collection: {VECTOR_DB_CONFIG['collection_name']}")
        
        return collection
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector database"""
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc['id'])
            texts.append(doc['text'])
            metadatas.append(doc['metadata'])
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to vector database")
    
    def search(self, query: str, n_results: int = None, 
               filter_metadata: Dict = None) -> List[Dict]:
        """Search for similar documents"""
        
        n_results = n_results or VECTOR_DB_CONFIG['max_results']
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    def search_by_component(self, component_name: str, query: str, 
                          n_results: int = 3) -> List[Dict]:
        """Search for information about a specific component"""
        
        filter_metadata = {"component": component_name}
        return self.search(query, n_results, filter_metadata)
    
    def search_by_category(self, category: str, query: str, 
                         n_results: int = 5) -> List[Dict]:
        """Search for information within a component category"""
        
        filter_metadata = {"category": category}
        return self.search(query, n_results, filter_metadata)
    
    def get_component_info(self, component_name: str) -> List[Dict]:
        """Get all information about a specific component"""
        
        results = self.collection.get(
            where={"component": component_name}
        )
        
        formatted_results = []
        for i in range(len(results['ids'])):
            formatted_results.append({
                'id': results['ids'][i],
                'text': results['documents'][i],
                'metadata': results['metadatas'][i]
            })
        
        return formatted_results
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        
        count = self.collection.count()
        
        # Get all metadata to analyze
        all_results = self.collection.get()
        
        # Count by category and component
        categories = {}
        components = {}
        data_types = {}
        
        for metadata in all_results['metadatas']:
            category = metadata.get('category', 'unknown')
            component = metadata.get('component', 'unknown')
            data_type = metadata.get('data_type', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            components[component] = components.get(component, 0) + 1
            data_types[data_type] = data_types.get(data_type, 0) + 1
        
        return {
            'total_documents': count,
            'categories': categories,
            'components': components,
            'data_types': data_types
        }
    
    def reset_database(self):
        """Reset the entire database"""
        
        self.client.delete_collection(VECTOR_DB_CONFIG['collection_name'])
        self.collection = self._get_or_create_collection()
        logger.info("Database reset completed")

class RAGSystem:
    """Retrieval Augmented Generation system"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
    
    def retrieve_context(self, query: str, component: str = None, 
                        category: str = None, n_results: int = 5) -> str:
        """Retrieve relevant context for a query"""
        
        if component:
            results = self.vector_db.search_by_component(component, query, n_results)
        elif category:
            results = self.vector_db.search_by_category(category, query, n_results)
        else:
            results = self.vector_db.search(query, n_results)
        
        # Format context
        context_parts = []
        for result in results:
            context_parts.append(f"[{result['metadata']['component']}] {result['text']}")
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, query: str, context: str, 
                         model = None) -> str:
        """Generate response using retrieved context"""
        
        # This is a simple implementation
        # In a full system, you would use a language model here
        
        prompt = f"""
        Based on the following hardware information, answer the question:
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        
        # For now, return formatted context
        # In practice, you would pass this to a language model
        return f"Based on the available information:\n\n{context}"
    
    def answer_question(self, query: str, component: str = None, 
                       category: str = None) -> Dict[str, Any]:
        """Complete RAG pipeline for answering questions"""
        
        # Retrieve relevant context
        context = self.retrieve_context(query, component, category)
        
        # Generate response
        response = self.generate_response(query, context)
        
        return {
            'query': query,
            'context': context,
            'response': response,
            'component': component,
            'category': category
        }

def load_and_index_data():
    """Load processed data and create vector database"""
    
    # Initialize vector database
    vector_db = VectorDatabase()
    
    # Load embeddings data
    embeddings_file = PROCESSED_DATA_DIR / "embeddings_data.json"
    
    if embeddings_file.exists():
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            embeddings_data = json.load(f)
        
        # Check if database is empty
        if vector_db.collection.count() == 0:
            logger.info("Adding documents to vector database...")
            vector_db.add_documents(embeddings_data)
        else:
            logger.info("Vector database already contains documents")
    else:
        logger.error("No embeddings data found. Please run data processing first.")
        return None
    
    return vector_db

def main():
    """Main function for testing RAG system"""
    
    # Load and index data
    vector_db = load_and_index_data()
    
    if vector_db is None:
        return
    
    # Print database statistics
    stats = vector_db.get_database_stats()
    logger.info(f"Database stats: {stats}")
    
    # Initialize RAG system
    rag_system = RAGSystem(vector_db)
    
    # Test queries
    test_queries = [
        "What pins does ESP32 have?",
        "How do I connect DHT22 sensor?",
        "Show me code example for Arduino Uno",
        "What is the voltage requirement for HC-SR04?",
        "How does MPU6050 work?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        result = rag_system.answer_question(query)
        logger.info(f"Response: {result['response'][:200]}...")

if __name__ == "__main__":
    main()
