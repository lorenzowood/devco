import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devdoc.storage import DevDocStorage


class TestDevDocStorage:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init_creates_devdoc_directory(self, temp_dir):
        """Test that init creates .devdoc directory with required files"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        devdoc_dir = Path(temp_dir) / '.devdoc'
        assert devdoc_dir.exists()
        assert devdoc_dir.is_dir()
    
    def test_init_creates_config_file(self, temp_dir):
        """Test that init creates config.json with default settings"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        config_file = Path(temp_dir) / '.devdoc' / 'config.json'
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert 'embedding_model' in config
        assert 'version' in config
    
    def test_init_creates_principles_file(self, temp_dir):
        """Test that init creates principles.json"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        principles_file = Path(temp_dir) / '.devdoc' / 'principles.json'
        assert principles_file.exists()
        
        with open(principles_file) as f:
            principles = json.load(f)
        
        assert isinstance(principles, list)
        assert len(principles) == 0
    
    def test_init_creates_summary_file(self, temp_dir):
        """Test that init creates summary.json"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        summary_file = Path(temp_dir) / '.devdoc' / 'summary.json'
        assert summary_file.exists()
        
        with open(summary_file) as f:
            summary = json.load(f)
        
        assert 'summary' in summary
        assert 'sections' in summary
        assert isinstance(summary['sections'], dict)
    
    def test_init_creates_database(self, temp_dir):
        """Test that init creates SQLite database"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        db_file = Path(temp_dir) / '.devdoc' / 'devdoc.db'
        assert db_file.exists()
    
    def test_init_creates_env_file(self, temp_dir):
        """Test that init creates .env file in .devdoc directory"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        env_file = Path(temp_dir) / '.devdoc' / '.env'
        assert env_file.exists()
        
        with open(env_file) as f:
            content = f.read()
        
        assert 'GOOGLE_API_KEY=' in content
    
    def test_init_twice_does_not_overwrite(self, temp_dir):
        """Test that running init twice doesn't overwrite existing config"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        # Modify config
        config_file = Path(temp_dir) / '.devdoc' / 'config.json'
        with open(config_file) as f:
            config = json.load(f)
        config['test_key'] = 'test_value'
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Init again
        storage.init()
        
        # Check that custom config is preserved
        with open(config_file) as f:
            config = json.load(f)
        assert config['test_key'] == 'test_value'