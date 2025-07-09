# RevAI

A multi-agentic Python CLI application for Code Review and finding bugs before merging branches.

## Agent Architecture

![Alt text][images/architecture.png]

## Examples

- File `diff_example` contains a ready git diff example that was tested
- File `output.md` demonstrates the output format of the application

## Getting started

1. Install **git** and **ripgrep**:
```bash
sudo apt install git ripgrep
```
2. Clone the repo

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

5. Add observability with LangSmith:
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
export LANGSMITH_API_KEY="your_langsmith_api_key"
export LANGSMITH_PROJECT="your_langsmith_project"
```

6. Set optional environment variables:
```bash
export LOGS_DIR=logs
```

7. Run the application:
```bash
python main.py
```

## Receive more info

```bash
python main.py -h 
```

## Run ETL

1. Add files with data in `dummy_knowledge` folder
2. Run:
```bash
python scripts/load_knowledge.py
```



