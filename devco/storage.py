"""
Storage module for devco - handles .devco directory structure and data persistence
"""
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class DevDocStorage:
    """Manages the .devco directory and all persistent storage"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.devco_dir = self.project_root / ".devco"
        
    def init(self):
        """Initialize the .devco directory structure"""
        # Create .devco directory
        self.devco_dir.mkdir(exist_ok=True)
        
        # Create config.json if it doesn't exist
        config_file = self.devco_dir / "config.json"
        if not config_file.exists():
            config = {
                "version": "0.1.0",
                "embedding_model": "gemini-embedding-exp-03-07-2048",
                "chunk_size": 500,
                "chunk_overlap": 50
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Create principles.json if it doesn't exist
        principles_file = self.devco_dir / "principles.json"
        if not principles_file.exists():
            with open(principles_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Create summary.json if it doesn't exist
        summary_file = self.devco_dir / "summary.json"
        if not summary_file.exists():
            summary = {
                "summary": "",
                "sections": {}
            }
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
        
        # Create SQLite database if it doesn't exist
        db_file = self.devco_dir / "devco.db"
        if not db_file.exists():
            conn = sqlite3.connect(db_file)
            # Create embeddings table
            conn.execute("""
                CREATE TABLE embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    content_id TEXT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create index for faster lookups
            conn.execute("CREATE INDEX idx_content ON embeddings(content_type, content_id)")
            conn.commit()
            conn.close()
        
        # Create .env file if it doesn't exist
        env_file = self.devco_dir / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# devco environment variables\n")
                f.write("GOOGLE_API_KEY=\n")
                f.write("# Uncomment and set your preferred embedding model:\n")
                f.write("# DEVCO_EMBEDDING_MODEL=gemini-embedding-exp-03-07-2048\n")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        config_file = self.devco_dir / "config.json"
        if not config_file.exists():
            raise FileNotFoundError("devco not initialized. Run 'devco init' first.")
        
        with open(config_file) as f:
            return json.load(f)
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to config.json"""
        config_file = self.devco_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Auto-commit changes
        self._git_commit_devco_changes("update config")
    
    def load_principles(self) -> List[str]:
        """Load principles from principles.json"""
        principles_file = self.devco_dir / "principles.json"
        if not principles_file.exists():
            raise FileNotFoundError("devco not initialized. Run 'devco init' first.")
        
        with open(principles_file) as f:
            return json.load(f)
    
    def save_principles(self, principles: List[str]):
        """Save principles to principles.json"""
        principles_file = self.devco_dir / "principles.json"
        with open(principles_file, 'w') as f:
            json.dump(principles, f, indent=2)
        
        # Auto-commit changes
        if len(principles) == 0:
            self._git_commit_devco_changes("clear principles")
        else:
            self._git_commit_devco_changes("update principles")
    
    def load_summary(self) -> Dict[str, Any]:
        """Load summary from summary.json"""
        summary_file = self.devco_dir / "summary.json"
        if not summary_file.exists():
            raise FileNotFoundError("devco not initialized. Run 'devco init' first.")
        
        with open(summary_file) as f:
            return json.load(f)
    
    def save_summary(self, summary: Dict[str, Any]):
        """Save summary to summary.json"""
        summary_file = self.devco_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Auto-commit changes
        self._git_commit_devco_changes("update summary")
    
    def get_db_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database"""
        db_file = self.devco_dir / "devco.db"
        if not db_file.exists():
            raise FileNotFoundError("devco not initialized. Run 'devco init' first.")
        
        return sqlite3.connect(db_file)
    
    def is_initialized(self) -> bool:
        """Check if devco is initialized in the current directory"""
        return (self.devco_dir.exists() and 
                (self.devco_dir / "config.json").exists() and
                (self.devco_dir / "devco.db").exists())
    
    def _is_git_repo(self) -> bool:
        """Check if we're in a git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True, cwd=self.project_root)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _git_commit_devco_changes(self, action: str, details: str = ""):
        """Commit devco file changes with proper staging isolation"""
        if not self._is_git_repo():
            return
        
        try:
            # Get current staging area state
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            staged_files = [f for f in result.stdout.strip().split('\n') if f] if result.stdout.strip() else []
            
            # Unstage all currently staged files
            if staged_files:
                subprocess.run(['git', 'reset'] + staged_files, 
                             capture_output=True, cwd=self.project_root)
            
            # Stage only devco files that have changed
            devco_files = ['.devco/config.json', '.devco/principles.json', 
                          '.devco/summary.json', '.devco/devco.db']
            
            files_to_stage = []
            for file_path in devco_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    # Check if file has changes
                    result = subprocess.run(['git', 'status', '--porcelain', file_path], 
                                          capture_output=True, text=True, cwd=self.project_root)
                    if result.stdout.strip():  # File has changes
                        files_to_stage.append(file_path)
            
            # Stage and commit devco changes if any
            if files_to_stage:
                subprocess.run(['git', 'add'] + files_to_stage, 
                             capture_output=True, cwd=self.project_root)
                
                commit_message = f"devco: {action}"
                if details:
                    commit_message += f" - {details}"
                
                subprocess.run(['git', 'commit', '-m', commit_message], 
                             capture_output=True, cwd=self.project_root)
            
            # Restage original files
            if staged_files:
                subprocess.run(['git', 'add'] + staged_files, 
                             capture_output=True, cwd=self.project_root)
        
        except Exception:
            # Silent failure - don't break devco if git operations fail
            pass