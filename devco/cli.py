#!/usr/bin/env python3
"""
devco - Project documentation and context management tool
"""
import argparse
import sys


def create_parser():
    """Create the argument parser for devco"""
    parser = argparse.ArgumentParser(
        prog='devco',
        description='Project documentation and context management tool'
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init command
    subparsers.add_parser('init', help='Initialize devco in a project')
    
    # principles commands
    principles_parser = subparsers.add_parser('principles', help='Manage project principles')
    principles_subparsers = principles_parser.add_subparsers(dest='principles_action')
    add_principle = principles_subparsers.add_parser('add', help='Add a new principle')
    add_principle.add_argument('--text', help='Principle text')
    principles_subparsers.add_parser('clear', help='Reset the principles')
    
    rm_parser = principles_subparsers.add_parser('rm', help='Remove a principle by number')
    rm_parser.add_argument('number', type=int, help='Principle number to remove')
    
    # summary commands
    summary_parser = subparsers.add_parser('summary', help='Manage project summary')
    summary_subparsers = summary_parser.add_subparsers(dest='summary_action')
    replace_summary = summary_subparsers.add_parser('replace', help='Replace the summary text')
    replace_summary.add_argument('--text', help='Summary text')
    
    # section commands  
    section_parser = subparsers.add_parser('section', help='Manage project sections')
    section_subparsers = section_parser.add_subparsers(dest='section_action', help='Section commands')
    
    show_section = section_subparsers.add_parser('show', help='Show a specific section')
    show_section.add_argument('name', help='Section name')
    
    add_section = section_subparsers.add_parser('add', help='Add a new section')
    add_section.add_argument('name', help='Section name')
    add_section.add_argument('--summary', help='Section summary')
    add_section.add_argument('--detail', help='Section detail')
    
    replace_section = section_subparsers.add_parser('replace', help='Replace section content')
    replace_section.add_argument('name', help='Section name')
    replace_section.add_argument('--summary', help='Section summary')
    replace_section.add_argument('--detail', help='Section detail')
    
    rm_section = section_subparsers.add_parser('rm', help='Remove a section')
    rm_section.add_argument('name', help='Section name')
    
    # Special handling for 'devco section name' shorthand - we'll handle this in the main function
    
    # embed command
    embed_parser = subparsers.add_parser('embed', help='Generate embeddings for all content')
    embed_parser.add_argument('--model', help='Embedding model to use (also updates .env)')
    
    # query command
    query_parser = subparsers.add_parser('query', help='Query the devco content')
    query_parser.add_argument('text', help='Query text')
    query_parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    query_parser.add_argument('--update-embeddings', action='store_true', help='Update embeddings for any missing content before querying')
    
    # Hidden embed-all command for background processing
    embed_all_parser = subparsers.add_parser('_embed-all', help=argparse.SUPPRESS)
    
    return parser


def cmd_init():
    """Initialize devco in the current project"""
    from .storage import DevDocStorage
    
    storage = DevDocStorage()
    
    if storage.is_initialized():
        print("devco is already initialized in this project.")
        return
    
    try:
        storage.init()
        print("✓ devco initialized successfully!")
        print("  Created .devco/ directory with:")
        print("  - config.json (configuration)")
        print("  - principles.json (development principles)")
        print("  - summary.json (project summary and sections)")
        print("  - devco.db (embeddings database)")
        print("  - .env (environment variables)")
        print("")
        print("Next steps:")
        print("1. Add your GOOGLE_API_KEY to .devco/.env")
        print("2. Add development principles: devco principles add")
        print("3. Set project summary: devco summary replace")
    except Exception as e:
        print(f"Error initializing devco: {e}")
        sys.exit(1)


def main():
    """Main entry point for the devco CLI"""
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
            if hasattr(args, 'text') and args.text:
                principles_manager.add_principle_with_text(args.text)
            else:
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
            if hasattr(args, 'text') and args.text:
                summary_manager.replace_summary(args.text)
            else:
                summary_manager.replace_summary()
    elif args.command == 'section':
        from .storage import DevDocStorage
        from .sections import SectionsManager
        
        storage = DevDocStorage()
        sections_manager = SectionsManager(storage)
        
        if args.section_action is None:
            print("Section command requires an action")
            print("Usage:")
            print("  devco section add <name> [--summary TEXT] [--detail TEXT]")
            print("  devco section show <name>")  
            print("  devco section replace <name> [--summary TEXT] [--detail TEXT]")
            print("  devco section rm <name>")
            sys.exit(1)
        elif args.section_action == 'show':
            sections_manager.show_section(args.name)
        elif args.section_action == 'add':
            if hasattr(args, 'summary') and args.summary and hasattr(args, 'detail') and args.detail:
                sections_manager.add_section_with_content(args.name, args.summary, args.detail)
            else:
                sections_manager.add_section(args.name)
        elif args.section_action == 'replace':
            if hasattr(args, 'summary') and args.summary and hasattr(args, 'detail') and args.detail:
                sections_manager.replace_section_with_content(args.name, args.summary, args.detail)
            else:
                sections_manager.replace_section(args.name)
        elif args.section_action == 'rm':
            sections_manager.remove_section(args.name)
    elif args.command == 'embed':
        from .storage import DevDocStorage
        from .embeddings import EmbeddingsManager
        
        storage = DevDocStorage()
        if not storage.is_initialized():
            print("devco not initialized. Run 'devco init' first.")
            sys.exit(1)
        
        embeddings_manager = EmbeddingsManager(storage)
        
        # Update model if provided
        if hasattr(args, 'model') and args.model:
            config = storage.load_config()
            config['embedding_model'] = args.model
            storage.save_config(config)
            
            # Update .env file with model
            env_file = storage.devco_dir / ".env"
            env_lines = []
            model_found = False
            
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.strip().startswith('DEVCO_EMBEDDING_MODEL='):
                            env_lines.append(f"DEVCO_EMBEDDING_MODEL={args.model}\n")
                            model_found = True
                        else:
                            env_lines.append(line)
            
            if not model_found:
                env_lines.append(f"DEVCO_EMBEDDING_MODEL={args.model}\n")
            
            with open(env_file, 'w') as f:
                f.writelines(env_lines)
            
            print(f"Updated embedding model to: {args.model}")
        
        print("Generating embeddings for all content...")
        embeddings_manager.embed_all_content()
    elif args.command == 'query':
        from .storage import DevDocStorage
        from .embeddings import EmbeddingsManager
        
        storage = DevDocStorage()
        if not storage.is_initialized():
            print("devco not initialized. Run 'devco init' first.")
            sys.exit(1)
        
        embeddings_manager = EmbeddingsManager(storage)
        
        # Check embedding status
        status = embeddings_manager.check_embeddings_status()
        
        # Handle --update-embeddings flag
        if hasattr(args, 'update_embeddings') and args.update_embeddings:
            if status["missing_content"]:
                print("Updating embeddings for new content...")
                embeddings_manager.embed_all_content()
        
        # Check if we have any embeddings at all
        elif not status["has_embeddings"]:
            if hasattr(args, 'json') and args.json:
                import json
                print(json.dumps({"query": args.text, "results": [], "warning": "No embeddings found. Use --update-embeddings or run 'devco embed' first."}))
            else:
                print("Warning: No embeddings found. Use --update-embeddings or run 'devco embed' first.")
                print("No similar content found.")
            return
        
        # Check for missing embeddings  
        elif status["missing_content"]:
            missing_count = len(status["missing_content"])
            if not (hasattr(args, 'json') and args.json):
                print(f"Note: {missing_count} content items don't have embeddings yet. Use --update-embeddings to include them.")
        
        results = embeddings_manager.search_similar_content(args.text, limit=5)
        
        if not results:
            if hasattr(args, 'json') and args.json:
                import json
                print(json.dumps({"query": args.text, "results": []}))
            else:
                print("No similar content found.")
            return
        
        if hasattr(args, 'json') and args.json:
            import json
            output = {
                "query": args.text,
                "results": results
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Similar content for query: '{args.text}'")
            print("=" * 50)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. [{result['content_type']}] {result['content_id']} (similarity: {result['similarity']:.3f})")
                print(f"   {result['chunk_text'][:200]}{'...' if len(result['chunk_text']) > 200 else ''}")
    elif args.command == '_embed-all':
        # Hidden command for background embedding
        from .storage import DevDocStorage
        from .embeddings import EmbeddingsManager
        
        storage = DevDocStorage()
        if storage.is_initialized():
            embeddings_manager = EmbeddingsManager(storage)
            embeddings_manager.embed_all_content(silent=True)
    else:
        # No command provided
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()