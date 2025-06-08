import pytest
import tempfile
import os
import sys
import sqlite3
import numpy as np
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devco.storage import DevDocStorage
from devco.embeddings import EmbeddingsManager


class TestEmbeddingsManager:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = DevDocStorage(tmpdir)
            storage.init()
            yield tmpdir
    
    @pytest.fixture
    def embeddings_manager(self, temp_dir):
        storage = DevDocStorage(temp_dir)
        return EmbeddingsManager(storage)
    
    def test_chunk_text(self, embeddings_manager):
        """Test text chunking functionality"""
        text = "This is a long piece of text. " * 50  # Create long text
        chunks = embeddings_manager.chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 120 for chunk in chunks)  # 100 + 20 overlap
        
        # Test overlap
        if len(chunks) > 1:
            # Check that chunks have some overlap
            assert chunks[0][-10:] in chunks[1][:30]
    
    @patch('subprocess.run')
    def test_generate_embeddings(self, mock_run, embeddings_manager):
        """Test embedding generation using llm command"""
        # Mock the llm embed command response
        mock_embedding = "[0.1, 0.2, 0.3, -0.1, 0.5]"
        mock_run.return_value = MagicMock(
            stdout=mock_embedding,
            stderr="",
            returncode=0
        )
        
        text = "Test text for embedding"
        embedding = embeddings_manager.generate_embedding(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 5
        assert embedding == [0.1, 0.2, 0.3, -0.1, 0.5]
    
    @patch('subprocess.run')
    def test_generate_embeddings_error(self, mock_run, embeddings_manager):
        """Test handling of embedding generation errors"""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Error: Invalid API key",
            returncode=1
        )
        
        text = "Test text"
        embedding = embeddings_manager.generate_embedding(text)
        
        assert embedding is None
    
    def test_store_embedding(self, embeddings_manager):
        """Test storing embeddings in database"""
        embedding = [0.1, 0.2, 0.3, -0.1, 0.5]
        
        embeddings_manager.store_embedding(
            content_type="principle",
            content_id="1",
            chunk_text="Test principle text",
            embedding=embedding
        )
        
        # Verify embedding was stored
        conn = embeddings_manager.storage.get_db_connection()
        cursor = conn.execute(
            "SELECT content_type, content_id, chunk_text FROM embeddings WHERE content_type=? AND content_id=?",
            ("principle", "1")
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "principle"
        assert result[1] == "1"
        assert result[2] == "Test principle text"
    
    def test_compute_similarity(self, embeddings_manager):
        """Test cosine similarity computation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        vec3 = [1.0, 0.0, 0.0]
        
        # Orthogonal vectors should have similarity ~0
        similarity = embeddings_manager.compute_similarity(vec1, vec2)
        assert abs(similarity) < 0.01
        
        # Identical vectors should have similarity 1
        similarity = embeddings_manager.compute_similarity(vec1, vec3)
        assert abs(similarity - 1.0) < 0.01
    
    @patch('devco.embeddings.EmbeddingsManager.generate_embedding')
    def test_embed_all_content(self, mock_generate, embeddings_manager):
        """Test embedding all content from storage"""
        # Setup test data
        storage = embeddings_manager.storage
        storage.save_principles(["Principle 1", "Principle 2"])
        storage.save_summary({
            "summary": "Test summary",
            "sections": {
                "test_section": {
                    "summary": "Section summary",
                    "detail": "Section detail"
                }
            }
        })
        
        # Mock embedding generation
        mock_generate.return_value = [0.1, 0.2, 0.3]
        
        embeddings_manager.embed_all_content()
        
        # Verify embeddings were generated for all content
        assert mock_generate.call_count >= 4  # principles + summary + section
        
        # Verify embeddings were stored
        conn = storage.get_db_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM embeddings")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count >= 4
    
    @patch('devco.embeddings.EmbeddingsManager.generate_embedding')
    def test_search_similar_content(self, mock_generate, embeddings_manager):
        """Test searching for similar content"""
        # Store some test embeddings
        embeddings_manager.store_embedding("principle", "1", "Test principle", [1.0, 0.0, 0.0])
        embeddings_manager.store_embedding("summary", "main", "Test summary", [0.0, 1.0, 0.0])
        embeddings_manager.store_embedding("section", "test", "Test section", [0.9, 0.1, 0.0])
        
        # Mock query embedding
        mock_generate.return_value = [1.0, 0.0, 0.0]
        
        results = embeddings_manager.search_similar_content("test query", limit=2)
        
        assert len(results) <= 2
        assert all('similarity' in result for result in results)
        assert all('content_type' in result for result in results)
        assert all('chunk_text' in result for result in results)
        
        # Results should be sorted by similarity (highest first)
        if len(results) > 1:
            assert results[0]['similarity'] >= results[1]['similarity']