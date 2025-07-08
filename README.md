# RevAI

An agentic Python application that provides intelligent analysis of git branch changes before merging. 

## Features

- **Multi-Agent Analysis**: Tech Lead agent supervises specialized agents for comprehensive code review
- **Interactive Chat Mode**: Guided git diff analysis with conversational interface
- **CLI Mode**: Direct command-line analysis for automation and scripts
- **Docker Support**: Fully containerized with Ollama integration
- **Comprehensive Reports**: Security, performance, architecture, and documentation insights

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"

# Run analysis
python main.py /path/to/project feature-branch main output.md

```

## Usage

### CLI Mode

```bash
# Basic analysis
python main.py /path/to/project feature-branch main output.md

# Verbose output
python main.py /path/to/project feature-branch main output.md --verbose

# Custom model and Ollama URL
python main.py /path/to/project feature-branch main output.md --model codellama:7b --ollama-url http://localhost:11434
```

### Interactive Chat Mode

```bash
# Start interactive session
python main.py --interactive

# Interactive with custom model
python main.py --interactive --model codellama:7b --ollama-url http://localhost:11434

# In chat mode, you can:
# - Ask questions about specific changes
# - Request detailed analysis of particular files
# - Get explanations of security or performance concerns
# - Receive suggestions for improvements
```

## Configuration

### Environment Variables

- `OLLAMA_URL`: Ollama service URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use (default: `llama3.2`)
- `LOGS_DIR`: Log file directory (default: `./logs`)
