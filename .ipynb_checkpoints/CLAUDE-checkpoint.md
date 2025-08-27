# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python data analysis project focused on analyzing telecommunications subscriber and pricing plan data from CSV files. The project uses pandas for data processing and provides both command-line and Jupyter notebook interfaces for interactive analysis.

## Development Environment Setup

### Virtual Environment (Required)
This project uses a Python virtual environment. Always activate it before working:

```bash
# Activate the virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt
```

### Dependencies
Core dependencies are defined in `requirements.txt`:
- pandas>=1.3.0 (primary data analysis)
- jupyter>=1.0.0 (notebook interface)
- matplotlib>=3.5.0 (basic plotting)
- seaborn>=0.11.0 (statistical visualization)
- plotly>=5.0.0 (interactive visualization)

## Common Development Commands

### Running the Analysis
```bash
# Console analysis program (outputs to terminal and database.md)
python csv_analyzer.py

# Jupyter Notebook (interactive analysis)
jupyter notebook
# Then open csv_analysis.ipynb in the browser

# Jupyter Lab (alternative interface)
pip install jupyterlab  # if not installed
jupyter lab
```

### File Management
```bash
# Check CSV files structure
ls -la csv/

# View generated analysis results
cat database.md
```

## Code Architecture

### Core Components

**csv_analyzer.py** - Main analysis engine
- `CSVAnalyzer` class: Handles CSV loading, analysis, and markdown report generation
- Automatic encoding detection (supports UTF-8, CP949, EUC-KR)
- Generates comprehensive `database.md` reports with statistics and sample data
- Memory usage and performance tracking

**csv_analysis.ipynb** - Interactive Jupyter notebook
- Multi-step analysis workflow with visualizations
- Interactive charts using matplotlib, seaborn, and plotly
- Korean language support with proper font configuration
- Comprehensive data exploration and insights generation

### Data Structure
```
csv/
├── ENTR_BY_INS.csv     # M-2 subscriber info (270K+ records, 111 columns)
├── ENTR_INT_INS.csv    # M-1 new subscriber info (38K+ records, 106 columns)  
└── MVNO_PRD_PLC.csv    # Pricing plan info (138 records, 9 columns)
```

### Key Analysis Features
- **Encoding Handling**: Robust CSV loading with multiple encoding fallbacks
- **Memory Optimization**: Large dataset processing with memory usage monitoring
- **Statistical Analysis**: Comprehensive descriptive statistics and data profiling
- **Visualization**: Multiple chart types (histograms, box plots, pie charts, interactive plots)
- **Report Generation**: Automated markdown report creation with timestamp tracking

## Data Analysis Workflow

1. **Data Loading**: Multi-encoding CSV parsing with error handling
2. **Data Profiling**: Column analysis, data types, missing values, memory usage
3. **Statistical Analysis**: Descriptive statistics for numerical columns
4. **Visualization**: Distribution analysis and relationship exploration
5. **Report Generation**: Structured markdown output to `database.md`

## File-Specific Notes

### csv_analyzer.py:30-70
The CSVAnalyzer class handles robust CSV loading with file-specific encoding preferences and automatic fallback mechanisms.

### csv_analysis.ipynb
- Uses Korean font configuration for matplotlib: `plt.rcParams['font.family'] = 'AppleGothic'`
- Implements interactive plotly visualizations for enhanced data exploration
- Includes comprehensive data relationship analysis between M-1, M-2, and pricing data

## Testing and Quality

This project does not include formal unit tests. Testing is done through:
- Data validation in the CSVAnalyzer class
- Sample data verification in notebooks
- Output validation in generated reports

## Output Files

- **database.md**: Auto-generated comprehensive analysis report
- **Notebook outputs**: Interactive visualizations and analysis results embedded in jupyter cells

## Important Notes

- CSV files contain Korean text and require proper encoding handling
- Large datasets (270K+ records) require memory-efficient processing
- Analysis results are automatically timestamped in generated reports
- Virtual environment is essential due to specific package version requirements