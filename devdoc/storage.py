"""
Storage module for devdoc - handles .devdoc directory structure and data persistence
"""
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, List


class DevDocStorage:
    """Manages the .devdoc directory and all persistent storage"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.devdoc_dir = self.project_root / ".devdoc"
        
    def init(self):
        """Initialize the .devdoc directory structure"""
        # Create .devdoc directory
        self.devdoc_dir.mkdir(exist_ok=True)
        
        # Create config.json if it doesn't exist
        config_file = self.devdoc_dir / "config.json"
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
        principles_file = self.devdoc_dir / "principles.json"
        if not principles_file.exists():
            with open(principles_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Create summary.json if it doesn't exist
        summary_file = self.devdoc_dir / "summary.json"
        if not summary_file.exists():
            summary = {
                "summary": "",
                "sections": {}
            }
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
        
        # Create SQLite database if it doesn't exist
        db_file = self.devdoc_dir / "devdoc.db"
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
        env_file = self.devdoc_dir / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# devdoc environment variables\n")
                f.write("GOOGLE_API_KEY=\n")
                f.write("# Uncomment and set your preferred embedding model:\n")
                f.write("# DEVDOC_EMBEDDING_MODEL=gemini-embedding-exp-03-07-2048\n")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        config_file = self.devdoc_dir / "config.json"
        if not config_file.exists():
            raise FileNotFoundError("devdoc not initialized. Run 'devdoc init' first.")
        
        with open(config_file) as f:
            return json.load(f)
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to config.json"""
        config_file = self.devdoc_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_principles(self) -> List[str]:
        """Load principles from principles.json"""
        principles_file = self.devdoc_dir / "principles.json"
        if not principles_file.exists():
            raise FileNotFoundError("devdoc not initialized. Run 'devdoc init' first.")
        
        with open(principles_file) as f:
            return json.load(f)
    
    def save_principles(self, principles: List[str]):
        """Save principles to principles.json"""
        principles_file = self.devdoc_dir / "principles.json"
        with open(principles_file, 'w') as f:
            json.dump(principles, f, indent=2)
    
    def load_summary(self) -> Dict[str, Any]:
        """Load summary from summary.json"""
        summary_file = self.devdoc_dir / "summary.json"
        if not summary_file.exists():
            raise FileNotFoundError("devdoc not initialized. Run 'devdoc init' first.")
        
        with open(summary_file) as f:
            return json.load(f)
    
    def save_summary(self, summary: Dict[str, Any]):
        """Save summary to summary.json"""
        summary_file = self.devdoc_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def get_db_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database"""
        db_file = self.devdoc_dir / "devdoc.db"
        if not db_file.exists():
            raise FileNotFoundError("devdoc not initialized. Run 'devdoc init' first.")
        
        return sqlite3.connect(db_file)
    
    def is_initialized(self) -> bool:
        """Check if devdoc is initialized in the current directory"""
        return (self.devdoc_dir.exists() and 
                (self.devdoc_dir / "config.json").exists() and
                (self.devdoc_dir / "devdoc.db").exists())