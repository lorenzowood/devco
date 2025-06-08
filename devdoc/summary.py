"""
Summary management for devdoc
"""
from typing import Dict, Any
from .storage import DevDocStorage


class SummaryManager:
    """Manages project summary and sections"""
    
    def __init__(self, storage: DevDocStorage):
        self.storage = storage
    
    def show_summary(self):
        """Show the current project summary and sections"""
        try:
            data = self.storage.load_summary()
            
            print("Project Summary:")
            print("=" * 50)
            
            if data.get('summary', '').strip():
                print(data['summary'])
            else:
                print("No summary defined yet. Set one with: devdoc summary replace")
            
            print("\nSections:")
            print("-" * 20)
            
            sections = data.get('sections', {})
            if sections:
                for name, content in sections.items():
                    print(f"\n{name}:")
                    if content.get('summary'):
                        print(f"  Summary: {content['summary']}")
                    if content.get('detail'):
                        print(f"  Detail: {content['detail']}")
            else:
                print("No sections defined yet. Add one with: devdoc section add <name>")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
    
    def replace_summary(self):
        """Replace the project summary with new content"""
        try:
            summary_text = input("Enter project summary: ").strip()
            
            if not summary_text:
                print("Summary cannot be empty.")
                return
            
            # Load existing data
            data = self.storage.load_summary()
            data['summary'] = summary_text
            
            # Save updated data
            self.storage.save_summary(data)
            
            print("Summary updated successfully.")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")