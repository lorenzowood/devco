# devdoc

> A CLI tool that helps AI assistants understand projects by managing persistent documentation, principles, and context through embeddings and RAG querying.

## 🎯 Problem

AI assistants lose context when working on projects across sessions. They waste time re-exploring codebases, re-learning project structure, and rediscovering development practices with every new conversation.

## ✨ Solution

devdoc creates persistent, searchable project knowledge that survives context resets:

- **Development Principles** - Your team's coding standards and practices
- **Project Summary** - High-level project description and purpose  
- **Technical Sections** - Detailed implementation guides with function names, file paths, and examples
- **RAG Search** - Semantic search across all documentation using vector embeddings

## 🚀 Quick Start

### Installation

```bash
pip install devdoc
```

### Initialize in your project

```bash
devdoc init
```

### Add your development principles

```bash
devdoc principles add --text "Follow Test-Driven Development"
devdoc principles add --text "Keep functions under 20 lines"
```

### Document your project

```bash
devdoc summary replace --text "FastAPI web service for user authentication with PostgreSQL backend"

devdoc section add architecture \
  --summary "Clean architecture with dependency injection" \
  --detail "Entry point: main.py:create_app() line 15. Uses FastAPI with dependency injection via Depends(). Database models in models/ directory. Business logic in services/ with UserService.create_user() method."
```

### Generate embeddings for semantic search

```bash
devdoc embed
```

### Query your documentation

```bash
devdoc query "how does authentication work"
devdoc query "testing approach"
devdoc query "database schema"
```

## 📚 Full Documentation

### View all content

```bash
devdoc summary          # Show project summary and all sections
devdoc principles       # List development principles
devdoc section show testing  # Show specific section
```

### Manage principles

```bash
devdoc principles                              # List all
devdoc principles add --text "New principle"   # Add with flag
devdoc principles add                          # Add interactively  
devdoc principles rm 2                         # Remove by number
devdoc principles clear                        # Remove all
```

### Manage summary

```bash
devdoc summary                                # Show current
devdoc summary replace --text "New summary"   # Replace with flag
devdoc summary replace                        # Replace interactively
```

### Manage sections

```bash
devdoc section show architecture              # Show specific section
devdoc section add testing \
  --summary "TDD with pytest" \
  --detail "Tests in tests/ directory. Run: pytest -v"
devdoc section replace api --summary "..." --detail "..."
devdoc section rm outdated-section
```

### Search and embeddings

```bash
devdoc embed                    # Generate embeddings for all content
devdoc query "database setup"   # Semantic search
devdoc query "testing framework" 
```

## 🏗️ Why This Works

### For AI Assistants

Instead of this inefficient pattern:
```
AI: Let me search through your files to understand the project...
AI: *uses grep, find, reads multiple files*
AI: *tries to infer patterns and practices*
AI: OK, I think I understand how this works...
```

You get this efficient pattern:
```
AI: devdoc query "testing approach"
AI: Perfect! I can see you use pytest with TDD methodology, 
    tests are in tests/ directory, and I should follow the 
    pattern in tests/test_user.py:test_create_user() line 25.
```

### For Development Teams

- **Onboarding**: New developers get instant project context
- **Consistency**: Shared principles ensure consistent code
- **Documentation**: Implementation details with specific examples
- **Knowledge Retention**: Project knowledge survives team changes

## 🔧 Technical Details

### Architecture

- **CLI Framework**: argparse with subcommands
- **Storage**: JSON files + SQLite for vector embeddings  
- **Embeddings**: Gemini via `llm` package for consistent results
- **Search**: Cosine similarity with chunked content and overlap

### File Structure

```
.devdoc/
├── config.json      # Settings and embedding model
├── principles.json  # Development principles  
├── summary.json     # Project summary and sections
├── devdoc.db       # SQLite database with embeddings
└── .env           # API keys (git-ignored)
```

### Requirements

- Python 3.8+
- `llm` package with Gemini plugin
- Google API key for embeddings

## ⚙️ Configuration

### Set up embeddings

1. Install the llm package: `pip install llm llm-gemini`
2. Add your Google API key to `.devdoc/.env`:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
3. Generate embeddings: `devdoc embed`

### Embedding Models

Configure in `.devdoc/config.json`:
```json
{
  "embedding_model": "gemini-embedding-exp-03-07-2048",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

## 📖 Best Practices

### Documentation Content

✅ **Include specific details:**
- Function names: `UserService.authenticate()` 
- File paths: `src/auth/service.py:45`
- Command examples: `pytest tests/test_auth.py -v`
- Code snippets and patterns

✅ **Write for AI assistants:**
- Assume no prior context
- Include implementation details
- Specify exact locations and examples

❌ **Avoid vague descriptions:**
- "We use good practices" → Specify what practices
- "Tests are important" → Specify testing framework and patterns
- "Code is modular" → Specify module structure and key classes

### Principles

Good principles are specific and actionable:
- ✅ "Use pytest fixtures for database setup in tests/conftest.py"
- ✅ "API endpoints follow REST patterns with serializers in api/serializers.py"
- ❌ "Write good code"
- ❌ "Be consistent"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow TDD: write tests first
4. Ensure all tests pass: `pytest -v`
5. Update documentation with specific implementation details
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Documentation](https://github.com/yourusername/devdoc/wiki)
- [Issues](https://github.com/yourusername/devdoc/issues)
- [Changelog](https://github.com/yourusername/devdoc/releases)