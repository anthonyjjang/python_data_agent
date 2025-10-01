# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
uv run streamlit run app.py
```

### Testing Components
```bash
# Test LLM functions
python test_app_functions.py

# Test Ollama connection
python test_ollama.py

# Test logging system
python test_logging.py
```

### Dependencies Management
```bash
# Add new dependencies
uv add <package_name>

# Install all dependencies
uv sync
```

### Ollama Local LLM Setup
```bash
# Start Ollama server
ollama serve

# Download recommended models
ollama pull qwen2.5:3b
ollama pull qwen2.5:7b
ollama pull llama3.2:3b

# Check installed models
ollama list
```

## Architecture

This is a **Streamlit-based Excel/CSV data analysis agent** that uses both OpenAI and local Ollama LLMs to answer questions about uploaded data files.

### Core Architecture Pattern
The application follows a **3-stage pipeline** for processing user queries:

1. **Code Generation**: LLM generates Python pandas code based on user query and data preview
2. **Code Execution**: Generated code is executed with error handling and automatic retry/correction
3. **Answer Generation**: Results are formatted into natural language response

### Key Components

**LLM Integration** (`app.py:57-284`):
- Dual LLM support: OpenAI (cloud) and Ollama (local)
- Automatic fallback: Ollama prioritized, falls back to OpenAI
- Model selection via Streamlit sidebar
- Robust error handling with detailed logging

**Data Processing Pipeline**:
- `generate_code_prompt()`: Creates prompts for pandas code generation
- `extract_code_from_response()`: Extracts executable code from LLM responses using multiple regex patterns
- `execute_generated_code()`: Executes code with automatic retry and error correction (up to 3 attempts)
- `generate_final_prompt()`: Formats results for natural language response

**File Handling** (`app.py:287-311`):
- Multi-encoding CSV support (UTF-8, EUC-KR, CP949, Latin1)
- Excel file support via openpyxl
- Automatic encoding detection when chardet is available

**Session Management**:
- LLM service and model selection stored in `st.session_state`
- Automatic service detection and preference (Ollama > OpenAI)

### Error Handling Strategy
- **Cascading encoding attempts** for CSV files
- **Multi-attempt code execution** with LLM-based error correction
- **Comprehensive logging** to app.log with UTF-8 encoding
- **User-friendly error messages** with troubleshooting hints

### Environment Setup
Requires `.env` file with:
```env
OPENAI_API_KEY=your_api_key_here
```

### Dependencies
Core dependencies managed via uv (Python 3.13+):
- streamlit: Web interface
- pandas: Data manipulation
- openai: Cloud LLM integration  
- python-dotenv: Environment management
- openpyxl: Excel file support