# devco

> A CLI tool that helps AI assistants understand projects by managing persistent documentation, principles, and context through embeddings and RAG querying.

## 🎯 Problem

AI assistants lose context when working on projects across sessions. They waste time re-exploring codebases, re-learning project structure, and rediscovering development practices with every new conversation.

## ✨ Solution

devco creates persistent, searchable project knowledge that survives context resets:

- **Development Principles** - Your team's coding standards and practices
- **Project Summary** - High-level project description and purpose  
- **Technical Sections** - Detailed implementation guides with function names, file paths, and examples
- **RAG Search** - Semantic search across all documentation using vector embeddings

## 🚀 Quick Start

### Installation

```bash
pip install devco
```

### Initialize in your project

```bash
devco init
```

### Add your development principles

```bash
devco principles add --text "Follow Test-Driven Development"
devco principles add --text "Keep functions under 20 lines"
devco principles add --text "Use specific function names and file paths in documentation"
```

### Document your project

```bash
devco summary replace --text "FastAPI web service for user authentication with PostgreSQL backend"

devco section add architecture \
  --summary "Clean architecture with dependency injection" \
  --detail "Entry point: main.py:create_app() line 15. Uses FastAPI with dependency injection via Depends(). Database models in models/ directory. Business logic in services/ with UserService.create_user() method."

devco section add testing \
  --summary "TDD with pytest and comprehensive isolation" \
  --detail "Tests in tests/ directory. Run: pytest -v. Key patterns: TestCase classes with temp_dir fixtures, @patch decorators for mocking, isolated DevDocStorage(tmpdir) per test. Example: test_add_principle() in tests/test_principles.py:33."
```

### Generate embeddings for semantic search

```bash
devco embed
```

### Query your documentation

```bash
devco query "how does authentication work"
devco query "testing approach"
devco query "database schema"
```

## 🤖 For AI Developers

### Essential Workflow

When working with AI assistants on any project, establish this pattern:

1. **Initialize devco immediately**: `devco init`
2. **Document as you go**: After each feature/change, update relevant sections
3. **Query before exploring**: `devco query "topic"` before searching files
4. **Capture user feedback**: Document requirements and future work

### AI Assistant Best Practices

✅ **Start every session with:**
```bash
devco summary    # Understand the project
devco principles # Know the coding standards
```

✅ **Before implementing features:**
```bash
devco query "authentication"      # Find existing patterns
devco query "database models"     # Understand data layer
devco query "testing framework"   # Follow test patterns
```

✅ **After implementing features:**
```bash
devco section add feature_name \
  --summary "Brief description" \
  --detail "Implementation details with function names, file paths, and usage examples"
```

### Real-World Example

Instead of:
```
AI: Let me explore your codebase to understand how you handle user authentication...
[reads 10+ files, makes assumptions]
```

Use:
```
AI: devco query "authentication"
AI: Perfect! I can see you use JWT tokens with UserService.authenticate() 
    in src/auth/service.py:45, and tests follow the pattern in 
    tests/test_auth.py:test_login_success().
```

## 📚 Full Documentation

### View all content

```bash
devco summary          # Show project summary and all sections
devco principles       # List development principles
devco section show testing  # Show specific section
```

### Manage principles

```bash
devco principles                              # List all
devco principles add --text "New principle"   # Add with flag
devco principles add                          # Add interactively  
devco principles rm 2                         # Remove by number
devco principles clear                        # Remove all
```

### Manage summary

```bash
devco summary                                # Show current
devco summary replace --text "New summary"   # Replace with flag
devco summary replace                        # Replace interactively
```

### Manage sections

```bash
devco section show architecture              # Show specific section
devco section add testing \
  --summary "TDD with pytest" \
  --detail "Tests in tests/ directory. Run: pytest -v"
devco section replace api --summary "..." --detail "..."
devco section rm outdated-section
```

### Search and embeddings

```bash
devco embed                    # Generate embeddings for all content
devco query "database setup"   # Semantic search
devco query "testing framework" 
```

### Git Integration (New in v0.1.8)

devco automatically commits all documentation changes to git:

```bash
devco principles add --text "New principle"
# → Creates git commit: "devco: update principles"

devco summary replace --text "Updated project description"  
# → Creates git commit: "devco: update summary"

devco section add feature --summary "..." --detail "..."
# → Creates git commit: "devco: update summary"
```

**Features:**
- **Automatic commits**: Every devco change creates a descriptive git commit
- **Staging preservation**: Your staged files remain untouched
- **Safe operation**: Only commits devco files, ignores non-git projects
- **Clean history**: Each devco action gets its own commit with clear messages

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
AI: devco query "testing approach"
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
- **Git Integration**: Automatic commits for all devco changes with staging preservation

### File Structure

```
.devco/
├── config.json      # Settings and embedding model
├── principles.json  # Development principles  
├── summary.json     # Project summary and sections
├── devco.db       # SQLite database with embeddings
└── .env           # API keys (git-ignored)
```

### Requirements

- Python 3.8+
- `llm` package with Gemini plugin
- Google API key for embeddings

## ⚙️ Configuration

### Set up embeddings

1. Install the llm package: `pip install llm llm-gemini`
2. Add your Google API key to `.devco/.env`:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
3. Generate embeddings: `devco embed`

### Embedding Models

Configure in `.devco/config.json`:
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

- [Documentation](https://github.com/yourusername/devco/wiki)
- [Issues](https://github.com/yourusername/devco/issues)
- [Changelog](https://github.com/yourusername/devco/releases)
