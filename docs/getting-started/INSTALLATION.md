# Installation Guide

Complete setup instructions for the Company Researcher system.

---

## Prerequisites

### Required Software

- **Python 3.11 or higher**
  - Check version: `python --version`
  - Download: [python.org](https://www.python.org/downloads/)

### Required API Keys

You'll need API keys from these services:

1. **Anthropic API** (Claude 3.5 Sonnet)
   - Sign up: [console.anthropic.com](https://console.anthropic.com/)
   - Cost: Pay-as-you-go (~$0.06 per research)
   - Free tier: $5 credit for new users

2. **Tavily API** (Web Search)
   - Sign up: [tavily.com](https://tavily.com/)
   - Cost: Free tier available (1,000 searches/month)
   - Paid: $0.001 per search

---

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd "Lang ai"
```

### 2. Create Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux**:
```bash
python -m venv venv
source venv/bin/activate
```

**Verify activation**:
- Your terminal prompt should show `(venv)` prefix
- Run `which python` (Mac/Linux) or `where python` (Windows) - should point to venv directory

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Expected packages**:
- `langgraph` - Agent orchestration
- `langchain` - LLM framework
- `anthropic` - Claude API
- `tavily-python` - Search API
- `python-dotenv` - Environment management

### 4. Configure Environment Variables

**Create .env file**:

```bash
# Copy example file
cp env.example .env
```

**Edit .env file** and add your API keys:

```bash
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here

# Optional Configuration
MAX_ITERATIONS=2
QUALITY_THRESHOLD=85.0
```

**Get your API keys**:

1. **Anthropic API Key**:
   - Go to [console.anthropic.com](https://console.anthropic.com/)
   - Sign in or create account
   - Navigate to "API Keys"
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-`)

2. **Tavily API Key**:
   - Go to [tavily.com](https://tavily.com/)
   - Sign up for account
   - Navigate to API section
   - Copy your API key

### 5. Verify Installation

```bash
# Test Python and packages
python -c "import langgraph, langchain, anthropic; print('All packages installed!')"

# Check environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API keys loaded!' if os.getenv('ANTHROPIC_API_KEY') else 'ERROR: API keys missing')"
```

---

## Directory Structure

After installation, your directory should look like:

```
Lang ai/
├── venv/                      # Virtual environment (created)
├── src/
│   └── company_researcher/    # Main package
│       ├── agents/            # Agent implementations
│       ├── workflows/         # LangGraph workflows
│       │   ├── basic_research.py
│       │   ├── multi_agent_research.py
│       │   └── parallel_agent_research.py
│       ├── state.py           # State management
│       ├── config.py          # Configuration
│       └── prompts.py         # Agent prompts
├── hello_research.py          # Entry point script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (created)
├── env.example                # Example environment file
├── outputs/                   # Research outputs (auto-created)
│   ├── reports/               # Markdown reports
│   └── logs/                  # Validation logs
└── docs/                      # Documentation
```

---

## Common Installation Issues

### Issue: "Python not found"

**Solution**:
```bash
# Windows: Add Python to PATH or use full path
C:\Python311\python.exe -m venv venv

# Mac: Install Python via Homebrew
brew install python@3.11
```

### Issue: "pip: command not found"

**Solution**:
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: "Permission denied" (Mac/Linux)

**Solution**:
```bash
# Don't use sudo, use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Module not found" after installation

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Issue: "API key not found" when running

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify .env contents (should have ANTHROPIC_API_KEY and TAVILY_API_KEY)
cat .env

# Make sure .env is in the same directory as hello_research.py
```

### Issue: "UnicodeEncodeError" with emoji characters (Windows)

**Problem**: Windows console (cmd.exe) can't display emoji characters used in progress output.

**Solution**:
```bash
# Option 1: Use Windows Terminal instead of cmd.exe
# Download from Microsoft Store

# Option 2: Set UTF-8 encoding in cmd.exe
chcp 65001

# Option 3: Use PowerShell instead
# PowerShell handles UTF-8 better than cmd.exe
```

**Note**: This is a known Windows console limitation and doesn't affect the research functionality - reports are still generated correctly.

---

## Testing Your Installation

### Quick Test

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Run a quick research
python hello_research.py "Microsoft"
```

**Expected output**:
```
🔬 Researching: Microsoft
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting research workflow...
  ✓ Researcher Agent: Gathering initial information...
  ✓ Quality Check: 82.0/100 (below threshold 85.0)
  ⟳ Iteration 2: Running specialist agents...
    ↻ Financial Agent: Analyzing financial data...
    ↻ Market Agent: Analyzing market position...
    ↻ Product Agent: Analyzing products...
  ✓ Synthesizer: Creating final report...
  ✓ Quality Check: 88.0/100 (meets threshold!)

✅ Research complete!
📊 Quality Score: 88.0/100
💰 Total Cost: $0.0386
📝 Report saved to: outputs/reports/microsoft_report.md
```

### Verify Output

```bash
# Check report was created
ls outputs/reports/

# View report
cat outputs/reports/microsoft_report.md
# or on Windows:
type outputs\reports\microsoft_report.md
```

---

## Next Steps

After successful installation:

1. **Read the Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
2. **Try more companies**: Research different companies
3. **Explore the documentation**: [docs/company-researcher/](docs/company-researcher/)
4. **Understand the architecture**: [docs/company-researcher/ARCHITECTURE.md](docs/company-researcher/ARCHITECTURE.md)

---

## Uninstallation

To completely remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# Remove outputs (optional)
rm -rf outputs/
```

---

## Getting Help

If you encounter issues:

1. Check [TROUBLESHOOTING.md](docs/company-researcher/TROUBLESHOOTING.md)
2. Review [FAQ.md](docs/company-researcher/FAQ.md)
3. Check [GitHub Issues](https://github.com/your-repo/issues)

---

**Installation complete!** Proceed to [QUICK_START.md](QUICK_START.md) to run your first research.
