import pytest
import tempfile
import os
import sys
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devdoc.storage import DevDocStorage
from devdoc.principles import PrinciplesManager


class TestPrinciplesManager:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = DevDocStorage(tmpdir)
            storage.init()
            yield tmpdir
    
    @pytest.fixture
    def principles_manager(self, temp_dir):
        storage = DevDocStorage(temp_dir)
        return PrinciplesManager(storage)
    
    def test_list_empty_principles(self, principles_manager):
        """Test listing principles when none exist"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.list_principles()
            output = mock_stdout.getvalue()
            assert "No principles defined yet" in output
    
    def test_add_principle(self, principles_manager):
        """Test adding a principle"""
        with patch('builtins.input', return_value='Always write tests first'):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                principles_manager.add_principle()
                output = mock_stdout.getvalue()
                assert "Added principle #1" in output
    
    def test_list_principles_after_adding(self, principles_manager):
        """Test listing principles after adding some"""
        # Add two principles
        with patch('builtins.input', side_effect=['Always write tests first', 'Keep code simple and readable']):
            principles_manager.add_principle()
            principles_manager.add_principle()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.list_principles()
            output = mock_stdout.getvalue()
            assert "1. Always write tests first" in output
            assert "2. Keep code simple and readable" in output
    
    def test_remove_principle(self, principles_manager):
        """Test removing a principle by number"""
        # Add two principles
        with patch('builtins.input', side_effect=['First principle', 'Second principle']):
            principles_manager.add_principle()
            principles_manager.add_principle()
        
        # Remove the first one
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.remove_principle(1)
            output = mock_stdout.getvalue()
            assert "Removed principle #1" in output
        
        # Check that only second principle remains, renumbered as #1
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.list_principles()
            output = mock_stdout.getvalue()
            assert "1. Second principle" in output
            assert "First principle" not in output
    
    def test_remove_nonexistent_principle(self, principles_manager):
        """Test removing a principle that doesn't exist"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.remove_principle(1)
            output = mock_stdout.getvalue()
            assert "No principle #1 found" in output
    
    def test_clear_principles(self, principles_manager):
        """Test clearing all principles"""
        # Add some principles
        with patch('builtins.input', side_effect=['First', 'Second', 'Third']):
            principles_manager.add_principle()
            principles_manager.add_principle()
            principles_manager.add_principle()
        
        # Clear them
        with patch('builtins.input', return_value='y'):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                principles_manager.clear_principles()
                output = mock_stdout.getvalue()
                assert "All principles cleared" in output
        
        # Verify they're gone
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.list_principles()
            output = mock_stdout.getvalue()
            assert "No principles defined yet" in output
    
    def test_clear_principles_cancelled(self, principles_manager):
        """Test cancelling clear operation"""
        # Add a principle
        with patch('builtins.input', return_value='Test principle'):
            principles_manager.add_principle()
        
        # Try to clear but cancel
        with patch('builtins.input', return_value='n'):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                principles_manager.clear_principles()
                output = mock_stdout.getvalue()
                assert "Cancelled" in output
        
        # Verify principle still exists
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            principles_manager.list_principles()
            output = mock_stdout.getvalue()
            assert "1. Test principle" in output