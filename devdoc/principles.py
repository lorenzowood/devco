"""
Principles management for devdoc
"""
from typing import List
from .storage import DevDocStorage


class PrinciplesManager:
    """Manages development principles for the project"""
    
    def __init__(self, storage: DevDocStorage):
        self.storage = storage
    
    def list_principles(self):
        """List all current principles"""
        try:
            principles = self.storage.load_principles()
            
            if not principles:
                print("No principles defined yet. Add one with: devdoc principles add")
                return
            
            print("Development Principles:")
            for i, principle in enumerate(principles, 1):
                print(f"{i}. {principle}")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
    
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
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
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
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
    
    def remove_principle(self, number: int):
        """Remove a principle by number"""
        try:
            principles = self.storage.load_principles()
            
            if number < 1 or number > len(principles):
                print(f"No principle #{number} found. Use 'devdoc principles' to see available principles.")
                return
            
            removed_principle = principles.pop(number - 1)
            self.storage.save_principles(principles)
            
            print(f"Removed principle #{number}: {removed_principle}")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
    
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
            else:
                print("Cancelled.")
        
        except FileNotFoundError:
            print("devdoc not initialized. Run 'devdoc init' first.")
        except KeyboardInterrupt:
            print("\nCancelled.")