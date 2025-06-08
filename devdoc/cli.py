#!/usr/bin/env python3
"""
devdoc - Project documentation and context management tool
"""
import argparse
import sys


def create_parser():
    """Create the argument parser for devdoc"""
    parser = argparse.ArgumentParser(
        prog='devdoc',
        description='Project documentation and context management tool'
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    subparsers.add_parser('init', help='Initialize devdoc in a project')
    
    # principles commands
    principles_parser = subparsers.add_parser('principles', help='Manage project principles')
    principles_subparsers = principles_parser.add_subparsers(dest='principles_action')
    principles_subparsers.add_parser('add', help='Add a new principle')
    principles_subparsers.add_parser('clear', help='Reset the principles')
    
    rm_parser = principles_subparsers.add_parser('rm', help='Remove a principle by number')
    rm_parser.add_argument('number', type=int, help='Principle number to remove')
    
    # summary commands
    summary_parser = subparsers.add_parser('summary', help='Manage project summary')
    summary_subparsers = summary_parser.add_subparsers(dest='summary_action')
    summary_subparsers.add_parser('replace', help='Replace the summary text')
    
    # section commands
    section_parser = subparsers.add_parser('section', help='Manage project sections')
    section_subparsers = section_parser.add_subparsers(dest='section_action')
    
    add_section = section_subparsers.add_parser('add', help='Add a new section')
    add_section.add_argument('name', help='Section name')
    
    replace_section = section_subparsers.add_parser('replace', help='Replace section content')
    replace_section.add_argument('name', help='Section name')
    
    rm_section = section_subparsers.add_parser('rm', help='Remove a section')
    rm_section.add_argument('name', help='Section name')
    
    # query command (any other argument)
    parser.add_argument('query', nargs='?', help='Query the devdoc content')
    
    return parser


def cmd_init():
    """Initialize devdoc in the current project"""
    from .storage import DevDocStorage
    
    storage = DevDocStorage()
    
    if storage.is_initialized():
        print("devdoc is already initialized in this project.")
        return
    
    try:
        storage.init()
        print("✓ devdoc initialized successfully!")
        print("  Created .devdoc/ directory with:")
        print("  - config.json (configuration)")
        print("  - principles.json (development principles)")
        print("  - summary.json (project summary and sections)")
        print("  - devdoc.db (embeddings database)")
        print("  - .env (environment variables)")
        print("")
        print("Next steps:")
        print("1. Add your GOOGLE_API_KEY to .devdoc/.env")
        print("2. Add development principles: devdoc principles add")
        print("3. Set project summary: devdoc summary replace")
    except Exception as e:
        print(f"Error initializing devdoc: {e}")
        sys.exit(1)


def main():
    """Main entry point for the devdoc CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == 'init':
        cmd_init()
    elif args.command == 'principles':
        from .storage import DevDocStorage
        from .principles import PrinciplesManager
        
        storage = DevDocStorage()
        principles_manager = PrinciplesManager(storage)
        
        if args.principles_action is None:
            # List principles
            principles_manager.list_principles()
        elif args.principles_action == 'add':
            principles_manager.add_principle()
        elif args.principles_action == 'rm':
            principles_manager.remove_principle(args.number)
        elif args.principles_action == 'clear':
            principles_manager.clear_principles()
    elif args.command == 'summary':
        from .storage import DevDocStorage
        from .summary import SummaryManager
        
        storage = DevDocStorage()
        summary_manager = SummaryManager(storage)
        
        if args.summary_action is None:
            # Show summary
            summary_manager.show_summary()
        elif args.summary_action == 'replace':
            summary_manager.replace_summary()
    elif args.command == 'section':
        if args.section_action is None:
            print("Section command requires an action")
            sys.exit(1)
        elif args.section_action == 'add':
            print(f"Adding section '{args.name}'...")
        elif args.section_action == 'replace':
            print(f"Replacing section '{args.name}'...")
        elif args.section_action == 'rm':
            print(f"Removing section '{args.name}'...")
    elif args.query:
        # Query command
        print(f"Querying: {args.query}")
    else:
        # No command provided
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()