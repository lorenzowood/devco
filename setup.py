from setuptools import setup, find_packages

setup(
    name="devdoc",
    version="0.1.0",
    description="Project documentation and context management tool",
    packages=find_packages(),
    install_requires=[
        "llm>=0.13.0",
        "llm-gemini",
        "sqlite-utils>=3.0.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.20.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "devdoc=devdoc.cli:main",
        ],
    },
    python_requires=">=3.8",
)