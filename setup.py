from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devco",
    version="0.1.7",
    author="Claude Code", 
    author_email="noreply@anthropic.com",
    description="A CLI tool that helps AI assistants understand projects through persistent documentation and RAG search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lorenzowood/devco",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "llm>=0.13.0",
        "llm-gemini",
        "sqlite-utils>=3.0.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "devco=devco.cli:main",
        ],
    },
    python_requires=">=3.8",
    keywords="documentation ai assistant rag vector search embeddings cli development",
    project_urls={
        "Bug Reports": "https://github.com/lorenzowood/devco/issues",
        "Source": "https://github.com/lorenzowood/devco",
        "Documentation": "https://github.com/lorenzowood/devco/wiki",
    },
)