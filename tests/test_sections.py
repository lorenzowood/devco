import pytest
import tempfile
import os
import sys
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devco.storage import DevDocStorage
from devco.sections import SectionsManager


class TestSectionsManager:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = DevDocStorage(tmpdir)
            storage.init()
            yield tmpdir
    
    @pytest.fixture
    def sections_manager(self, temp_dir):
        storage = DevDocStorage(temp_dir)
        return SectionsManager(storage)
    
    def test_show_nonexistent_section(self, sections_manager):
        """Test showing a section that doesn't exist"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.show_section("architecture")
            output = mock_stdout.getvalue()
            assert "Section 'architecture' not found" in output
    
    def test_add_section(self, sections_manager):
        """Test adding a new section"""
        section_name = "architecture"
        summary = "System architecture overview"
        detail = "The system uses a modular CLI design with separate managers for each feature."
        
        with patch('builtins.input', side_effect=[summary, detail]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                sections_manager.add_section(section_name)
                output = mock_stdout.getvalue()
                assert f"Added section '{section_name}'" in output
    
    def test_show_section_after_adding(self, sections_manager):
        """Test showing a section after it's been added"""
        section_name = "testing"
        summary = "Testing approach"
        detail = "We use pytest with TDD methodology for all components."
        
        # Add section
        with patch('builtins.input', side_effect=[summary, detail]):
            sections_manager.add_section(section_name)
        
        # Show section
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.show_section(section_name)
            output = mock_stdout.getvalue()
            assert f"Section: {section_name}" in output
            assert summary in output
            assert detail in output
    
    def test_replace_section(self, sections_manager):
        """Test replacing an existing section"""
        section_name = "database"
        
        # Add initial section
        with patch('builtins.input', side_effect=["Initial summary", "Initial detail"]):
            sections_manager.add_section(section_name)
        
        # Replace section
        new_summary = "Updated database design"
        new_detail = "Now using SQLite with embeddings table for vector storage."
        
        with patch('builtins.input', side_effect=[new_summary, new_detail]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                sections_manager.replace_section(section_name)
                output = mock_stdout.getvalue()
                assert f"Updated section '{section_name}'" in output
        
        # Verify replacement
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.show_section(section_name)
            output = mock_stdout.getvalue()
            assert new_summary in output
            assert new_detail in output
            assert "Initial" not in output
    
    def test_replace_nonexistent_section(self, sections_manager):
        """Test replacing a section that doesn't exist"""
        with patch('builtins.input', side_effect=["Summary", "Detail"]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                sections_manager.replace_section("nonexistent")
                output = mock_stdout.getvalue()
                assert "Section 'nonexistent' not found" in output
    
    def test_remove_section(self, sections_manager):
        """Test removing a section"""
        section_name = "api"
        
        # Add section
        with patch('builtins.input', side_effect=["API design", "REST API endpoints"]):
            sections_manager.add_section(section_name)
        
        # Remove section
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.remove_section(section_name)
            output = mock_stdout.getvalue()
            assert f"Removed section '{section_name}'" in output
        
        # Verify removal
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.show_section(section_name)
            output = mock_stdout.getvalue()
            assert "Section 'api' not found" in output
    
    def test_remove_nonexistent_section(self, sections_manager):
        """Test removing a section that doesn't exist"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            sections_manager.remove_section("nonexistent")
            output = mock_stdout.getvalue()
            assert "Section 'nonexistent' not found" in output
    
    def test_empty_section_input(self, sections_manager):
        """Test handling empty section input"""
        with patch('builtins.input', side_effect=["", ""]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                sections_manager.add_section("test")
                output = mock_stdout.getvalue()
                assert "Summary cannot be empty" in output or "Cancelled" in output
    
    def test_cancel_section_input(self, sections_manager):
        """Test cancelling section input with Ctrl+C"""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                sections_manager.add_section("test")
                output = mock_stdout.getvalue()
                assert "Cancelled" in output