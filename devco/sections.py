"""
Sections management for devco
"""
from typing import Dict, Any
from .storage import DevDocStorage


class SectionsManager:
    """Manages project sections with summary and detail content"""
    
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
    
    def show_section(self, section_name: str):
        """Show a specific section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found. Use 'devco section add {section_name}' to create it.")
                return
            
            section = sections[section_name]
            print(f"Section: {section_name}")
            print("=" * (len(section_name) + 9))
            
            if section.get('summary'):
                print(f"Summary: {section['summary']}")
            
            if section.get('detail'):
                print(f"\nDetail:\n{section['detail']}")
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def add_section(self, section_name: str):
        """Add a new section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name in sections:
                print(f"Section '{section_name}' already exists. Use 'devco section replace {section_name}' to update it.")
                return
            
            summary = input(f"Enter summary for section '{section_name}': ").strip()
            
            if not summary:
                print("Summary cannot be empty.")
                return
            
            detail = input(f"Enter detail for section '{section_name}': ").strip()
            
            # Add the section
            sections[section_name] = {
                'summary': summary,
                'detail': detail
            }
            
            data['sections'] = sections
            self.storage.save_summary(data)
            
            print(f"Added section '{section_name}' successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")
    
    def add_section_with_content(self, section_name: str, summary: str, detail: str):
        """Add a new section with provided content (non-interactive)"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name in sections:
                print(f"Section '{section_name}' already exists. Use 'devco section replace {section_name}' to update it.")
                return
            
            # Add the section
            sections[section_name] = {
                'summary': summary,
                'detail': detail
            }
            
            data['sections'] = sections
            self.storage.save_summary(data)
            
            print(f"Added section '{section_name}' successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def replace_section(self, section_name: str):
        """Replace an existing section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found. Use 'devco section add {section_name}' to create it.")
                return
            
            summary = input(f"Enter new summary for section '{section_name}': ").strip()
            
            if not summary:
                print("Summary cannot be empty.")
                return
            
            detail = input(f"Enter new detail for section '{section_name}': ").strip()
            
            # Update the section
            sections[section_name] = {
                'summary': summary,
                'detail': detail
            }
            
            data['sections'] = sections
            self.storage.save_summary(data)
            
            print(f"Updated section '{section_name}' successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")
    
    def replace_section_with_content(self, section_name: str, summary: str, detail: str):
        """Replace an existing section with provided content (non-interactive)"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found. Use 'devco section add {section_name}' to create it.")
                return
            
            # Update the section
            sections[section_name] = {
                'summary': summary,
                'detail': detail
            }
            
            data['sections'] = sections
            self.storage.save_summary(data)
            
            print(f"Updated section '{section_name}' successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")
    
    def remove_section(self, section_name: str):
        """Remove a section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found.")
                return
            
            del sections[section_name]
            data['sections'] = sections
            self.storage.save_summary(data)
            
            print(f"Removed section '{section_name}' successfully.")
            self._auto_embed()
        
        except FileNotFoundError:
            print("devco not initialized. Run 'devco init' first.")