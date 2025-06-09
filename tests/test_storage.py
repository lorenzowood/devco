import pytest
import tempfile
import os
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devco.storage import DevDocStorage


class TestDevDocStorage:
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init_creates_devco_directory(self, temp_dir):
        """Test that init creates .devco directory with required files"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        devco_dir = Path(temp_dir) / '.devco'
        assert devco_dir.exists()
        assert devco_dir.is_dir()
    
    def test_init_creates_config_file(self, temp_dir):
        """Test that init creates config.json with default settings"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        config_file = Path(temp_dir) / '.devco' / 'config.json'
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert 'embedding_model' in config
        assert 'version' in config
    
    def test_init_creates_principles_file(self, temp_dir):
        """Test that init creates principles.json"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        principles_file = Path(temp_dir) / '.devco' / 'principles.json'
        assert principles_file.exists()
        
        with open(principles_file) as f:
            principles = json.load(f)
        
        assert isinstance(principles, list)
        assert len(principles) == 0
    
    def test_init_creates_summary_file(self, temp_dir):
        """Test that init creates summary.json"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        summary_file = Path(temp_dir) / '.devco' / 'summary.json'
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
        
        db_file = Path(temp_dir) / '.devco' / 'devco.db'
        assert db_file.exists()
    
    def test_init_creates_env_file(self, temp_dir):
        """Test that init creates .env file in .devco directory"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        env_file = Path(temp_dir) / '.devco' / '.env'
        assert env_file.exists()
        
        with open(env_file) as f:
            content = f.read()
        
        assert 'GOOGLE_API_KEY=' in content
    
    def test_init_twice_does_not_overwrite(self, temp_dir):
        """Test that running init twice doesn't overwrite existing config"""
        storage = DevDocStorage(temp_dir)
        storage.init()
        
        # Modify config
        config_file = Path(temp_dir) / '.devco' / 'config.json'
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


class TestGitIntegration:
    """Test git auto-commit functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture 
    def git_repo(self, temp_dir):
        """Create a git repo in temp directory"""
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        return temp_dir

    def test_is_git_repo_true_in_git_directory(self, git_repo):
        """Test _is_git_repo returns True in git repository"""
        storage = DevDocStorage(git_repo)
        assert storage._is_git_repo() == True

    def test_is_git_repo_false_in_non_git_directory(self, temp_dir):
        """Test _is_git_repo returns False outside git repository"""
        storage = DevDocStorage(temp_dir)
        assert storage._is_git_repo() == False

    @patch('subprocess.run')
    def test_git_commit_devco_changes_not_in_git_repo(self, mock_run, temp_dir):
        """Test git commit does nothing when not in git repo"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        storage = DevDocStorage(temp_dir)
        
        # Should not raise exception and not call git commands after repo check
        storage._git_commit_devco_changes("test action")
        
        # Only the initial git repo check should be called
        mock_run.assert_called_once_with(['git', 'rev-parse', '--git-dir'], 
                                       capture_output=True, check=True, cwd=storage.project_root)

    def test_git_commit_preserves_staging_area(self, git_repo):
        """Test that git commit preserves user's staging area"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Create and stage a user file
        user_file = Path(git_repo) / "user_file.txt" 
        user_file.write_text("user content")
        subprocess.run(['git', 'add', 'user_file.txt'], cwd=git_repo, capture_output=True)
        
        # Check file is staged
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True, cwd=git_repo)
        assert 'user_file.txt' in result.stdout
        
        # Make a devco change
        storage.save_principles(['test principle'])
        
        # Check user file is still staged
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True, cwd=git_repo)
        assert 'user_file.txt' in result.stdout

    def test_git_commit_creates_commit_for_devco_changes(self, git_repo):
        """Test that devco changes create git commits"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Initial commit to have something to compare against
        subprocess.run(['git', 'add', '.devco/'], cwd=git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'initial devco setup'], cwd=git_repo, capture_output=True)
        
        # Make a devco change
        storage.save_principles(['test principle'])
        
        # Check that a new commit was created
        result = subprocess.run(['git', 'log', '--oneline', '-n', '2'], 
                              capture_output=True, text=True, cwd=git_repo)
        commits = result.stdout.strip().split('\n')
        
        assert len(commits) == 2
        assert 'devco: update principles' in commits[0]

    def test_git_commit_with_no_changes_does_nothing(self, git_repo):
        """Test that git commit does nothing when no devco files changed"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Initial commit
        subprocess.run(['git', 'add', '.devco/'], cwd=git_repo, capture_output=True) 
        subprocess.run(['git', 'commit', '-m', 'initial'], cwd=git_repo, capture_output=True)
        
        # Call git commit with no actual changes
        storage._git_commit_devco_changes("test action")
        
        # Should still have only one commit
        result = subprocess.run(['git', 'log', '--oneline'], 
                              capture_output=True, text=True, cwd=git_repo)
        commits = result.stdout.strip().split('\n')
        assert len(commits) == 1

    def test_save_principles_triggers_git_commit(self, git_repo):
        """Test that save_principles automatically commits changes"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Initial commit
        subprocess.run(['git', 'add', '.devco/'], cwd=git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'initial'], cwd=git_repo, capture_output=True)
        
        # Save principles should trigger commit
        storage.save_principles(['principle 1', 'principle 2'])
        
        # Check latest commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], 
                              capture_output=True, text=True, cwd=git_repo)
        assert result.stdout == 'devco: update principles'

    def test_save_summary_triggers_git_commit(self, git_repo):
        """Test that save_summary automatically commits changes"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Initial commit  
        subprocess.run(['git', 'add', '.devco/'], cwd=git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'initial'], cwd=git_repo, capture_output=True)
        
        # Save summary should trigger commit
        storage.save_summary({'summary': 'test summary', 'sections': {}})
        
        # Check latest commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], 
                              capture_output=True, text=True, cwd=git_repo)
        assert result.stdout == 'devco: update summary'

    def test_clear_principles_commit_message(self, git_repo):
        """Test that clearing principles has specific commit message"""
        storage = DevDocStorage(git_repo)
        storage.init()
        
        # Initial commit with principles
        storage.save_principles(['principle 1'])
        subprocess.run(['git', 'add', '.devco/'], cwd=git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'initial'], cwd=git_repo, capture_output=True)
        
        # Clear principles
        storage.save_principles([])
        
        # Check commit message is specific for clearing
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], 
                              capture_output=True, text=True, cwd=git_repo)
        assert result.stdout == 'devco: clear principles'