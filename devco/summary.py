"""
Summary management for devco
"""
from typing import Dict, Any
from .storage import DevDocStorage


class SummaryManager:
    """Manages project summary and sections"""
    
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
    
    def show_summary(self):
        """Show the current project summary and sections"""
        try:
            data = self.storage.load_summary()
            
            print("Project Summary:")
            print("=" * 50)
            
            if data.get('summary', '').strip():
                print(data['summary'])
            else:
                print("No summary defined yet. Set one with: devco summary replace")
            
            print("\nSections:")
            print("-" * 20)
            
            sections = data.get('sections', {})
            if sections:
                for name, content in sections.items():
                    print(f"\n{name}:")
                    if content.get('summary'):
                        print(f"  {content['summary']}")
                    else:
                        print("  No summary")
            else:
                print("No sections defined yet. Add one with: devco section add <name>")
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def replace_summary(self, text: str = None):
        """Replace the project summary with new content"""
        try:
            if text is None:
                summary_text = input("Enter project summary: ").strip()
            else:
                summary_text = text.strip()
            
            if not summary_text:
                print("Summary cannot be empty.")
                return
            
            # Load existing data
            data = self.storage.load_summary()
            data['summary'] = summary_text
            
            # Save updated data
            self.storage.save_summary(data)
            
            print("Summary updated successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")