# Agentic Text-to-SQL Framework

## Overview
A LangGraph-based agent for Text-to-SQL that inspects SQLite schemas, generates SQL queries, and validates results through automated self-correction. Runs locally on Gemma 4 via Ollama with no external API dependencies.

## Key Features
- **LangGraph orchestration** with multi-step pipeline (schema → query → validation)
- **Tool calling** for dynamic schema inspection
- **Local execution** on Gemma 4 via Ollama

## Architecture
- **LangGraph** for workflow orchestration
- **Multi-step pipeline** (schema retrieval → query generation → SQL validation)
- **Custom tool calling** for dynamic schema inspection
- **SQLite** read-only backend execution

## Results
- **64.1% accuracy** (663/1,034 queries) on Spider benchmark
- **20 diverse database schemas** evaluated
- **Local-first execution** with Gemma 4 via Ollama

## Installation and Usage

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) 

### Setup
```bash
# Install dependencies
uv sync

# Run evaluation
uv run main.py
```

## Dataset:
[Spider dataset (dev split)](https://yale-lily.github.io/spider)
```
```
@inproceedings{Yu&al.18c,
  title     = {Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task},
  author    = {Tao Yu and Rui Zhang and Kai Yang and Michihiro Yasunaga and Dongxu Wang and Zifan Li and James Ma and Irene Li and Qingning Yao and Shanelle Roman and Zilin Zhang and Dragomir Radev}
  booktitle = "Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing",
  address   = "Brussels, Belgium",
  publisher = "Association for Computational Linguistics",
  year      = 2018
}
```
```

### Project Structure
- `main.py`: Agent orchestration and evaluation loop
- `utils/database.py`: Database utils and tools
- `results.csv`: Evaluation results
