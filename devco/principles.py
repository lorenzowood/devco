"""
Principles management for devco
"""
from typing import List
from .storage import DevDocStorage


class PrinciplesManager:
    """Manages development principles for the project"""
    
    def __init__(self, storage: DevDocStorage):
        self.storage = storage
    
    def _auto_embed(self):
        """Automatically regenerate embeddings after content changes"""
        try:
            import subprocess
            import sys
            
            # Check if we have an API key configured
            env_file = self.storage.devco_dir / ".env"
            has_api_key = False
            
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.strip() and not line.startswith('#') and 'GOOGLE_API_KEY=' in line:
                            key_value = line.split('=', 1)[1].strip()
                            if key_value and key_value != '':
                                has_api_key = True
                                break
            
            if has_api_key:
                # Start detached subprocess for embedding
                subprocess.Popen(
                    [sys.executable, "-m", "devco.cli", "_embed-all"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # Detach from parent process
                )
            
        except Exception:
            pass  # Silent failure
    
    def list_principles(self):
        """List all current principles"""
        try:
            principles = self.storage.load_principles()
            
            if not principles:
                print("No principles defined yet. Add one with: devco principles add")
                return
            
            print("Development Principles:")
            for i, principle in enumerate(principles, 1):
                print(f"{i}. {principle}")
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def add_principle(self):
        """Add a new principle"""
        try:
            principle = input("Enter new principle: ").strip()
            
            if not principle:
                print("Principle cannot be empty.")
                return
            
            principles = self.storage.load_principles()
            principles.append(principle)
            self.storage.save_principles(principles)
            
            print(f"Added principle #{len(principles)}: {principle}")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")
    
    def add_principle_with_text(self, principle_text: str):
        """Add a new principle with provided text (non-interactive)"""
        try:
            if not principle_text.strip():
                print("Principle cannot be empty.")
                return
            
            principles = self.storage.load_principles()
            principles.append(principle_text.strip())
            self.storage.save_principles(principles)
            
            print(f"Added principle #{len(principles)}: {principle_text.strip()}")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def remove_principle(self, number: int):
        """Remove a principle by number"""
        try:
            principles = self.storage.load_principles()
            
            if number < 1 or number > len(principles):
                print(f"No principle #{number} found. Use 'devco principles' to see available principles.")
                return
            
            removed_principle = principles.pop(number - 1)
            self.storage.save_principles(principles)
            
            print(f"Removed principle #{number}: {removed_principle}")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def clear_principles(self):
        """Clear all principles after confirmation"""
        try:
            principles = self.storage.load_principles()
            
            if not principles:
                print("No principles to clear.")
                return
            
            confirm = input(f"Are you sure you want to clear all {len(principles)} principles? (y/N): ").strip().lower()
            
            if confirm in ('y', 'yes'):
                self.storage.save_principles([])
                print("All principles cleared.")
                self._auto_embed()
            else:
                print("Cancelled.")
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")