"""
Embeddings management for devco using llm package
"""
import json
import sqlite3
import subprocess
import math
import os
from typing import List, Dict, Any, Optional, Tuple
from .storage import DevDocStorage


class EmbeddingsManager:
    """Manages embeddings generation and vector search using llm package"""
    
    def __init__(self, storage: DevDocStorage):
        self.storage = storage
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for embedding"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at word boundary
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size - 50:  # Don't break too early
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using llm command"""
        try:
            config = self.storage.load_config()
            model = config.get('embedding_model', 'gemini-embedding-exp-03-07-2048')
            
            # Load environment variables from .env file
            env_file = self.storage.devco_dir / ".env"
            env_vars = os.environ.copy()
            
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            
            # Set the Gemini API key for llm if available
            if 'GOOGLE_API_KEY' in env_vars:
                env_vars['LLM_GEMINI_KEY'] = env_vars['GOOGLE_API_KEY']
            
            # Use llm embed command
            result = subprocess.run([
                'llm', 'embed', '-c', text, '-m', model
            ], capture_output=True, text=True, timeout=30, env=env_vars)
            
            if result.returncode != 0:
                print(f"Error generating embedding: {result.stderr}")
                return None
            
            # Parse the JSON array output
            embedding_str = result.stdout.strip()
            embedding = json.loads(embedding_str)
            
            return embedding
        
        except subprocess.TimeoutExpired:
            print("Embedding generation timed out")
            return None
        except json.JSONDecodeError:
            print(f"Failed to parse embedding output: {result.stdout}")
            return None
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def store_embedding(self, content_type: str, content_id: str, chunk_text: str, embedding: List[float]):
        """Store embedding in the database"""
        try:
            conn = self.storage.get_db_connection()
            
            # Convert embedding to blob
            embedding_blob = json.dumps(embedding).encode('utf-8')
            
            conn.execute("""
                INSERT INTO embeddings (content_type, content_id, chunk_text, embedding)
                VALUES (?, ?, ?, ?)
            """, (content_type, content_id, chunk_text, embedding_blob))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"Error storing embedding: {e}")
    
    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        try:
            # Compute dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Compute magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
        
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    def embed_all_content(self, silent=False):
        """Generate embeddings for all content in storage"""
        try:
            # Clear existing embeddings
            conn = self.storage.get_db_connection()
            conn.execute("DELETE FROM embeddings")
            conn.commit()
            conn.close()
            
            # Embed principles
            principles = self.storage.load_principles()
            for i, principle in enumerate(principles):
                chunks = self.chunk_text(principle)
                for j, chunk in enumerate(chunks):
                    embedding = self.generate_embedding(chunk)
                    if embedding:
                        self.store_embedding("principle", f"{i+1}", chunk, embedding)
            
            # Embed summary and sections
            summary_data = self.storage.load_summary()
            
            # Embed main summary
            if summary_data.get('summary'):
                chunks = self.chunk_text(summary_data['summary'])
                for j, chunk in enumerate(chunks):
                    embedding = self.generate_embedding(chunk)
                    if embedding:
                        self.store_embedding("summary", "main", chunk, embedding)
            
            # Embed sections
            sections = summary_data.get('sections', {})
            for section_name, section_data in sections.items():
                # Embed section summary
                if section_data.get('summary'):
                    embedding = self.generate_embedding(section_data['summary'])
                    if embedding:
                        self.store_embedding("section", section_name, section_data['summary'], embedding)
                
                # Embed section detail
                if section_data.get('detail'):
                    chunks = self.chunk_text(section_data['detail'])
                    for j, chunk in enumerate(chunks):
                        embedding = self.generate_embedding(chunk)
                        if embedding:
                            self.store_embedding("section", f"{section_name}_detail", chunk, embedding)
            
            if not silent:
                print("✓ All content embedded successfully")
        
        except Exception as e:
            print(f"Error embedding content: {e}")
    
    def search_similar_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for content similar to query using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                print("Failed to generate query embedding")
                return []
            
            # Get all stored embeddings
            conn = self.storage.get_db_connection()
            cursor = conn.execute("""
                SELECT content_type, content_id, chunk_text, embedding
                FROM embeddings
            """)
            
            results = []
            for row in cursor.fetchall():
                content_type, content_id, chunk_text, embedding_blob = row
                
                # Parse stored embedding
                stored_embedding = json.loads(embedding_blob.decode('utf-8'))
                
                # Compute similarity
                similarity = self.compute_similarity(query_embedding, stored_embedding)
                
                results.append({
                    'content_type': content_type,
                    'content_id': content_id,
                    'chunk_text': chunk_text,
                    'similarity': similarity
                })
            
            conn.close()
            
            # Sort by similarity (highest first) and limit results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
        
        except Exception as e:
            print(f"Error searching content: {e}")
            return []
    
    def check_embeddings_status(self) -> dict:
        """Check if embeddings exist for all content and return status"""
        try:
            status = {
                "has_embeddings": False,
                "missing_content": [],
                "total_content_items": 0,
                "embedded_items": 0
            }
            
            # Count content items
            principles = self.storage.load_principles()
            summary_data = self.storage.load_summary()
            sections = summary_data.get('sections', {})
            
            content_items = []
            content_items.extend([f"principle_{i+1}" for i in range(len(principles))])
            if summary_data.get('summary'):
                content_items.append("summary_main")
            for section_name in sections:
                content_items.append(f"section_{section_name}")
                content_items.append(f"section_{section_name}_detail")
            
            status["total_content_items"] = len(content_items)
            
            # Check what's in embeddings DB
            conn = self.storage.get_db_connection()
            cursor = conn.execute("SELECT DISTINCT content_type, content_id FROM embeddings")
            embedded_items = set()
            for row in cursor.fetchall():
                content_type, content_id = row
                embedded_items.add(f"{content_type}_{content_id}")
            conn.close()
            
            status["embedded_items"] = len(embedded_items)
            status["has_embeddings"] = len(embedded_items) > 0
            
            # Find missing items
            missing = []
            for item in content_items:
                if item not in embedded_items:
                    missing.append(item)
            
            status["missing_content"] = missing
            return status
            
        except Exception as e:
            return {
                "has_embeddings": False,
                "missing_content": [],
                "total_content_items": 0,
                "embedded_items": 0,
                "error": str(e)
            }