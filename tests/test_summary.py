import pytest
import tempfile
import os
import sys
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devdoc.storage import DevDocStorage
from devdoc.summary import SummaryManager


class TestSummaryManager:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = DevDocStorage(tmpdir)
            storage.init()
            yield tmpdir
    
    @pytest.fixture
    def summary_manager(self, temp_dir):
        storage = DevDocStorage(temp_dir)
        return SummaryManager(storage)
    
    def test_show_empty_summary(self, summary_manager):
        """Test showing summary when empty"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            summary_manager.show_summary()
            output = mock_stdout.getvalue()
            assert "Project Summary:" in output
            assert "No summary defined yet" in output
            assert "No sections defined yet" in output
    
    def test_replace_summary(self, summary_manager):
        """Test replacing project summary"""
        test_summary = "This is a CLI tool for managing project documentation and context."
        
        with patch('builtins.input', return_value=test_summary):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summary_manager.replace_summary()
                output = mock_stdout.getvalue()
                assert "Summary updated successfully" in output
    
    def test_show_summary_after_setting(self, summary_manager):
        """Test showing summary after it's been set"""
        test_summary = "This is a CLI tool for managing project documentation."
        
        # Set summary
        with patch('builtins.input', return_value=test_summary):
            summary_manager.replace_summary()
        
        # Show summary
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            summary_manager.show_summary()
            output = mock_stdout.getvalue()
            assert "Project Summary:" in output
            assert test_summary in output
    
    def test_single_line_summary_input(self, summary_manager):
        """Test entering a single line summary"""
        test_summary = "This is a single line summary for the project."
        
        with patch('builtins.input', return_value=test_summary):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summary_manager.replace_summary()
                output = mock_stdout.getvalue()
                assert "Summary updated successfully" in output
    
    def test_empty_summary_input(self, summary_manager):
        """Test handling empty summary input"""
        with patch('builtins.input', return_value=""):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summary_manager.replace_summary()
                output = mock_stdout.getvalue()
                assert "Summary cannot be empty" in output or "Cancelled" in output
    
    def test_cancel_summary_input(self, summary_manager):
        """Test cancelling summary input with Ctrl+C"""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summary_manager.replace_summary()
                output = mock_stdout.getvalue()
                assert "Cancelled" in output