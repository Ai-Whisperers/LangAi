# Troubleshooting Guide

Common issues and solutions for the Company Researcher system.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Runtime Errors](#runtime-errors)
- [Quality Issues](#quality-issues)
- [Cost Issues](#cost-issues)
- [Performance Issues](#performance-issues)
- [Windows-Specific Issues](#windows-specific-issues)

---

## Installation Issues

### Python Not Found

**Error**:
```
'python' is not recognized as an internal or external command
```

**Solution**:
```bash
# Windows: Use full path or add Python to PATH
C:\Python311\python.exe -m venv venv

# Mac: Install via Homebrew
brew install python@3.11

# Verify installation
python --version  # Should show 3.11 or higher
```

### pip Command Not Found

**Error**:
```
pip: command not found
```

**Solution**:
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt

# Or upgrade pip
python -m pip install --upgrade pip
```

### Permission Denied (Mac/Linux)

**Error**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Don't use sudo! Use virtual environment instead
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Module Not Found After Installation

**Error**:
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Verify you're in venv (should see (venv) in prompt)
which python  # Mac/Linux
where python  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Configuration Issues

### API Key Not Found

**Error**:
```
ValueError: Missing ANTHROPIC_API_KEY. Get your key at: https://console.anthropic.com/
```

**Solution**:
```bash
# 1. Check .env file exists
ls -la .env  # Mac/Linux
dir .env     # Windows

# 2. Verify .env contains API keys
cat .env     # Mac/Linux
type .env    # Windows

# Should show:
# ANTHROPIC_API_KEY=sk-ant-...
# TAVILY_API_KEY=tvly-...

# 3. If missing, create/update .env
cp env.example .env
# Then edit .env and add your API keys
```

### API Key Invalid

**Error**:
```
anthropic.AuthenticationError: Invalid API key
```

**Solution**:
```bash
# 1. Verify API key format
# Anthropic keys start with: sk-ant-
# Tavily keys start with: tvly-

# 2. Get new API key
# Anthropic: https://console.anthropic.com/
# Tavily: https://tavily.com/

# 3. Update .env file
# Make sure there are no extra spaces or quotes
# Wrong: ANTHROPIC_API_KEY = "sk-ant-..."
# Right: ANTHROPIC_API_KEY=sk-ant-...
```

### .env File Not Loading

**Error**:
API keys not found even though .env exists

**Solution**:
```bash
# 1. Ensure .env is in the same directory as hello_research.py
ls -la .env  # Should be in root directory

# 2. Check file encoding
# .env must be UTF-8, not UTF-16

# 3. Verify python-dotenv is installed
pip show python-dotenv

# 4. Test manually
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

---

## Runtime Errors

### UnicodeEncodeError (Windows)

**Error**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f52c' in position 0
```

**Cause**: Windows cmd.exe can't display emoji characters used in progress output

**Solution**:
```bash
# Option 1: Use Windows Terminal (recommended)
# Download from Microsoft Store

# Option 2: Set UTF-8 encoding in cmd.exe
chcp 65001
python hello_research.py "Tesla"

# Option 3: Use PowerShell instead
# PowerShell handles UTF-8 better than cmd.exe

# Option 4: Disable emojis (future feature)
```

**Note**: This doesn't affect functionality - reports are still generated correctly.

### No Search Results

**Error**:
```
[Financial] WARNING: No search results to analyze!
```

**Cause**: Tavily API returned no results or API quota exceeded

**Solution**:
```bash
# 1. Check Tavily API status
# Visit: https://tavily.com/

# 2. Verify API key is valid
# Test Tavily connection manually

# 3. Check API quota
# Tavily free tier: 1,000 searches/month

# 4. Try a different company
python hello_research.py "Microsoft"
```

### LLM Timeout

**Error**:
```
TimeoutError: Request to Anthropic API timed out
```

**Solution**:
```bash
# 1. Check internet connection
ping anthropic.com

# 2. Retry the research
# Temporary network issues are common

# 3. Check Anthropic status
# Visit: https://status.anthropic.com/

# 4. Reduce max_tokens if persistent
# Edit config.py: llm_max_tokens = 2000
```

### JSON Parsing Error

**Error**:
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Cause**: LLM returned malformed JSON

**Note**: The system has fallback handling for this

**Solution**:
```python
# This is usually handled gracefully by agents
# If you see this error in logs, it's expected
# Agents will use default values as fallback
```

### Report Not Generated

**Issue**: Research completes but no report file

**Solution**:
```bash
# 1. Check outputs directory exists
ls -la outputs/

# 2. Create directories if missing
mkdir -p outputs/reports
mkdir -p outputs/logs

# 3. Check permissions
# Ensure you have write permissions in outputs/

# 4. Check for error messages
# Review terminal output for errors

# 5. Verify report_path in output
python -c "
from company_researcher.workflows.parallel_agent_research import research_company
result = research_company('Tesla')
print(result['report_path'])
"
```

---

## Quality Issues

### Quality Always Below Threshold

**Issue**: Quality score consistently below 85%

**Current Performance**: 67% success rate (2 out of 3 companies reach 85%+)

**This is normal behavior!** Not all companies have sufficient public information.

**Understanding Quality Scores**:
- 90-100: Excellent - Comprehensive coverage
- 85-89: Good - Meets threshold ✅
- 70-84: Acceptable - Below threshold ⚠️
- <70: Poor - Significant gaps

**Why Quality Might Be Low**:
1. **Limited Public Information**: Private/stealth companies
2. **Recent Companies**: Startups with minimal history
3. **Complex Structures**: Conglomerates with many divisions
4. **Search API Limitations**: Tavily may not find niche sources

**What To Do**:
```bash
# 1. Check the report anyway
# Quality 78-84% is still useful!

# 2. Review missing_info in logs
# See what specific information was missing

# 3. Try researching again
# Search results can vary

# 4. Accept limitations
# Current system (Phase 4) isn't perfect
# Future phases will improve success rate
```

**Future Improvements** (Phases 7-19):
- More specialist agents for deeper analysis
- Enhanced search with multiple providers
- Better source verification

### Quality Check Costs Too Much

**Issue**: Quality check alone costs $0.01-0.02

**Explanation**:
- Quality check requires an LLM call
- It analyzes entire research + sources
- This is necessary for adaptive iteration

**Optimization Options**:
```python
# Future: Reduce quality check frequency
# Current: Runs after every iteration (Phase 4)

# Cost breakdown:
# - Initial research: $0.01-0.02
# - Quality check: $0.01-0.02
# - Specialists (if needed): $0.04-0.06
# - Synthesis: $0.01-0.02
# - Final quality check: $0.01-0.02
# Total: ~$0.08 average
```

---

## Cost Issues

### Cost Higher Than Expected

**Issue**: Research costs more than $0.08

**Normal Cost Range**: $0.02 - $0.15 depending on:
- Company complexity
- Number of iterations (1 or 2)
- Amount of search data

**Cost Breakdown**:
| Component | Cost | Percentage |
|-----------|------|------------|
| Initial Research | $0.01-0.02 | 12-25% |
| Quality Check | $0.01-0.02 | 12-25% |
| Specialists (if iteration) | $0.04-0.06 | 50-75% |
| Synthesis | $0.01-0.02 | 12-25% |

**Optimization Strategies**:

1. **Use Haiku Model** (already default):
```python
# config.py already uses Claude 3.5 Haiku
# Cheapest option: $0.80 per 1M input tokens
```

2. **Limit Iterations**:
```python
# Current max: 2 iterations
# Each iteration roughly doubles cost
```

3. **Future Caching** (Phases 11-12):
```python
# Planned: Cache search results
# Planned: Reuse company research
# Expected savings: 40-60% on repeat queries
```

### Cost Tracking Inaccurate

**Issue**: Reported costs don't match Anthropic dashboard

**Explanation**:
- System tracks Claude costs only
- Tavily search costs estimated (~$0.001 per search)
- Anthropic may have slight pricing variations
- Tax/fees not included

**Verification**:
```python
# Check cost calculation
from company_researcher.config import get_config

config = get_config()
pricing = config.get_model_pricing()
print(f"Input: ${pricing['input']} per 1M tokens")
print(f"Output: ${pricing['output']} per 1M tokens")

# Calculate for specific usage
cost = config.calculate_llm_cost(input_tokens=1000, output_tokens=500)
print(f"Cost for 1000 in / 500 out: ${cost:.6f}")
```

---

## Performance Issues

### Research Takes Too Long

**Issue**: Research takes >5 minutes

**Normal Duration**: 2-5 minutes per company

**Slow Performance Causes**:
1. **Slow Internet**: Search API calls
2. **High Token Usage**: Complex companies
3. **Iteration**: 2 iterations = ~2x time
4. **LLM Response Time**: Anthropic API latency

**Optimization**:
```bash
# 1. Check internet speed
# Tavily searches require fast connection

# 2. Reduce max_tokens
# Edit config.py: llm_max_tokens = 2000

# 3. Accept single iteration
# Modify should_continue_research to finish after 1 iteration

# 4. Use faster model (not recommended - costs more)
# config.llm_model = "claude-3-5-sonnet-20241022"
```

### Memory Usage High

**Issue**: Python process uses lots of RAM

**Cause**: Large search results kept in memory

**Solution**:
```bash
# Current: All search results kept in state
# This is necessary for specialist agents

# Future optimization (Phase 12):
# Context engineering to reduce state size
# Compression of search results
# Selective context passing
```

**Current Workaround**:
```python
# Limit search results
# Edit config.py:
max_search_results = 10  # Instead of 15
```

---

## Windows-Specific Issues

### Virtual Environment Activation

**Issue**: Can't activate virtual environment

**Solution**:
```bash
# If activation fails, try:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Then activate:
venv\Scripts\activate

# Verify:
where python  # Should show path in venv
```

### File Path Issues

**Issue**: Paths with spaces cause errors

**Solution**:
```bash
# Always quote paths with spaces
cd "C:\Users\Your Name\Documents\Lang ai"

# Or use short path
cd C:\PROGRA~1\...  # Use dir /x to see short names
```

### Line Ending Issues

**Issue**: Scripts have wrong line endings (^M characters)

**Solution**:
```bash
# Install dos2unix
# Or use git to fix:
git config --global core.autocrlf true

# Or manually:
# Open file in Notepad++
# Edit → EOL Conversion → Unix (LF)
```

---

## Debugging Tips

### Enable Verbose Logging

```python
# Add to config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check State at Any Point

```python
# Add debugging to any agent:
def my_agent_node(state: OverallState) -> Dict[str, Any]:
    print(f"\n[DEBUG] Current state:")
    print(f"  company_name: {state.get('company_name')}")
    print(f"  search_results: {len(state.get('search_results', []))} results")
    print(f"  total_cost: ${state.get('total_cost', 0.0):.4f}")
    # ... rest of agent
```

### Test Individual Agents

```python
# Test agent in isolation:
from company_researcher.state import create_initial_state
from company_researcher.agents.financial import financial_agent_node

state = create_initial_state("Tesla")
state["search_results"] = [...]  # Add mock data
result = financial_agent_node(state)
print(result)
```

### Inspect LangGraph Workflow

```python
# Visualize the graph:
from company_researcher.workflows.parallel_agent_research import create_parallel_agent_workflow

workflow = create_parallel_agent_workflow()

# Print graph structure
print(workflow.get_graph().draw_mermaid())
```

---

## Getting Help

### Documentation

- [User Guide](USER_GUIDE.md) - How to use the system
- [Architecture](ARCHITECTURE.md) - System design
- [Implementation](IMPLEMENTATION.md) - Code structure
- [FAQ](FAQ.md) - Frequently asked questions

### Logs

Check these files for detailed information:
- `outputs/logs/PHASE4_VALIDATION_SUMMARY.md` - System validation
- Terminal output - Agent progress and errors
- Anthropic Console - API usage and errors

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share experiences

---

## Next Steps

If you've tried these solutions and still have issues:

1. **Check System Status**:
   - [Anthropic Status](https://status.anthropic.com/)
   - [Tavily Status](https://tavily.com/)

2. **Review Logs**: Check terminal output and log files

3. **Test Components**:
   - Test API keys manually
   - Test individual agents
   - Verify dependencies

4. **Report Issue**: Include:
   - Error message
   - Steps to reproduce
   - System info (OS, Python version)
   - Minimal example

---

**Last Updated**: December 5, 2025
**Version**: 0.4.0 (Phase 4 Complete)
