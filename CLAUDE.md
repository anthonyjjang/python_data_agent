# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **comprehensive Python data analysis project** that combines:
1. **Streamlit-based conversational AI agent** for interactive data analysis
2. **Jupyter Notebook-based CSV analysis** for telecommunications data
3. **Dual LLM support** (OpenAI GPT and OLLAMA local models)

## Development Environment Setup

### Virtual Environment (Required)
This project uses a Python virtual environment. Always activate it before working:

```bash
# Activate the virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### Dependencies
Core dependencies are defined in `pyproject.toml` and `requirements.txt`:
- streamlit: Web interface for conversational analysis
- pandas: Data manipulation and analysis
- openai: Cloud LLM integration
- python-dotenv: Environment management
- openpyxl: Excel file support
- jupyter: Notebook interface
- matplotlib, seaborn, plotly: Visualization libraries

## Common Development Commands

### Running the Applications

#### Streamlit App (Conversational Analysis)
```bash
# Main Streamlit application
uv run streamlit run app.py

# Test LLM functions
python test_app_functions.py

# Test Ollama connection
python test_ollama.py

# Test logging system
python test_logging.py
```

#### Jupyter Notebook (Advanced Analysis)
```bash
# Jupyter Notebook (interactive analysis)
jupyter notebook
# Then open csv_analysis.ipynb in the browser

# Jupyter Lab (alternative interface)
pip install jupyterlab  # if not installed
jupyter lab
```

#### Console Analysis
```bash
# Console analysis program (outputs to terminal and database.md)
python csv_analyzer.py
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

### Core Architecture Pattern

The project follows **two distinct but complementary patterns**:

#### 1. Streamlit Conversational Agent (app.py)
**3-stage pipeline** for processing user queries:
1. **Code Generation**: LLM generates Python pandas code based on user query and data preview
2. **Code Execution**: Generated code is executed with error handling and automatic retry/correction
3. **Answer Generation**: Results are formatted into natural language response

#### 2. Jupyter Notebook Analysis (csv_analysis.ipynb)
**Multi-step analysis workflow**:
1. **Data Loading**: Multi-encoding CSV parsing with error handling
2. **Data Profiling**: Column analysis, data types, missing values, memory usage
3. **Statistical Analysis**: Descriptive statistics for numerical columns
4. **Visualization**: Distribution analysis and relationship exploration
5. **Report Generation**: Structured markdown output to `database.md`

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

**CSV Analysis Engine** (`csv_analyzer.py`):
- `CSVAnalyzer` class: Handles CSV loading, analysis, and markdown report generation
- Automatic encoding detection (supports UTF-8, CP949, EUC-KR)
- Generates comprehensive `database.md` reports with statistics and sample data
- Memory usage and performance tracking

### Data Structure
```
csv/
├── ENTR_BY_INS.csv     # M-2 subscriber info (270K+ records, 111 columns)
├── ENTR_INT_INS.csv    # M-1 new subscriber info (38K+ records, 106 columns)  
└── MVNO_PRD_PLC.csv    # Pricing plan info (138 records, 9 columns)
```

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

## File-Specific Notes

### app.py (Streamlit Application)
- **Lines 57-284**: LLM integration with dual support (OpenAI + OLLAMA)
- **Lines 312-354**: Code generation prompt creation
- **Lines 359-445**: Code extraction with multiple regex patterns
- **Lines 447-492**: Code execution with retry mechanism
- **Lines 498-511**: Final answer generation

### csv_analyzer.py (CSV Analysis Engine)
- **Lines 30-70**: CSVAnalyzer class with robust CSV loading
- **Lines 96-168**: Individual file analysis with comprehensive statistics
- **Lines 198-274**: Markdown report generation

### csv_analysis.ipynb (Jupyter Notebook)
- Uses Korean font configuration: `plt.rcParams['font.family'] = 'AppleGothic'`
- Implements interactive plotly visualizations
- Includes comprehensive data relationship analysis

## Testing and Quality

Testing is done through:
- **Streamlit app**: Interactive testing via web interface
- **Unit tests**: `test_app_functions.py`, `test_ollama.py`, `test_logging.py`
- **Data validation**: CSVAnalyzer class validation
- **Output validation**: Generated reports and visualizations

## Output Files

- **app.log**: Streamlit application logs
- **database.md**: Auto-generated comprehensive analysis report
- **Notebook outputs**: Interactive visualizations and analysis results
- **Column info**: CSV files with detailed column mappings

## Important Notes

- **Korean text support**: CSV files contain Korean text requiring proper encoding
- **Large datasets**: 270K+ records require memory-efficient processing
- **Dual LLM support**: Automatic fallback between OLLAMA and OpenAI
- **Virtual environment**: Essential due to specific package version requirements
- **Real-time analysis**: Streamlit provides immediate feedback and visualization