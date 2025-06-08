"""
Sections management for devdoc
"""
from typing import Dict, Any
from .storage import DevDocStorage


class SectionsManager:
    """Manages project sections with summary and detail content"""
    
    def __init__(self, storage: DevDocStorage):
        self.storage = storage
    
    def show_section(self, section_name: str):
        """Show a specific section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found. Use 'devdoc section add {section_name}' to create it.")
                return
            
            section = sections[section_name]
            print(f"Section: {section_name}")
            print("=" * (len(section_name) + 9))
            
            if section.get('summary'):
                print(f"Summary: {section['summary']}")
            
            if section.get('detail'):
                print(f"\nDetail:\n{section['detail']}")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
    
    def add_section(self, section_name: str):
        """Add a new section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name in sections:
                print(f"Section '{section_name}' already exists. Use 'devdoc section replace {section_name}' to update it.")
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
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")
    
    def replace_section(self, section_name: str):
        """Replace an existing section"""
        try:
            data = self.storage.load_summary()
            sections = data.get('sections', {})
            
            if section_name not in sections:
                print(f"Section '{section_name}' not found. Use 'devdoc section add {section_name}' to create it.")
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
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")
    
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
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")