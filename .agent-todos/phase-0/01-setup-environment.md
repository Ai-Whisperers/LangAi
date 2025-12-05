# Task: Environment Setup

**Phase:** 0
**Estimated Time:** 2 hours
**Dependencies:** None
**Status:** [x] Complete

## Context

Before we can build anything, we need a working development environment with all necessary tools and API access. This task ensures we can call Claude and Tavily APIs successfully.

## Prerequisites

- [ ] Windows/Mac/Linux machine with internet access
- [ ] Admin rights to install software
- [ ] Credit card for API signups (both have free tiers)

## Implementation Steps

### Step 1: Install Python 3.11+

**Goal:** Have Python 3.11 or higher installed and accessible from command line

**Actions:**
- [ ] Check current Python version: `python --version`
- [ ] If < 3.11, download from https://www.python.org/downloads/
- [ ] Install Python (make sure to check "Add Python to PATH")
- [ ] Verify installation: `python --version` should show 3.11+
- [ ] Verify pip: `pip --version` should work

**Verification:**
```bash
python --version  # Should show 3.11 or higher
pip --version     # Should show pip 23.0 or higher
```

### Step 2: Create Project Virtual Environment

**Goal:** Isolated Python environment for this project

**Actions:**
- [ ] Navigate to project directory
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate environment:
  - Windows: `venv\Scripts\activate`
  - Mac/Linux: `source venv/bin/activate`
- [ ] Verify activation (prompt should show `(venv)`)

**Verification:**
```bash
# After activation
which python  # Should point to venv/bin/python or venv\Scripts\python
pip list     # Should show minimal packages (pip, setuptools)
```

### Step 3: Get Anthropic API Key

**Goal:** Access to Claude 3.5 Sonnet API

**Actions:**
- [ ] Go to https://console.anthropic.com/
- [ ] Sign up or log in
- [ ] Navigate to API Keys section
- [ ] Create new API key
- [ ] Copy key (starts with `sk-ant-api03-...`)
- [ ] Test key with curl:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: YOUR_KEY_HERE" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }'
```

**Expected Response:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Hello! How can I assist you today?"}],
  ...
}
```

**Cost Check:**
- Free tier: $5 credit
- Claude 3.5 Sonnet pricing: ~$3/$15 per 1M tokens (input/output)
- Expected usage: ~$0.25 per research

### Step 4: Get Tavily API Key

**Goal:** Access to Tavily search API

**Actions:**
- [ ] Go to https://tavily.com/
- [ ] Sign up for account
- [ ] Navigate to API Keys in dashboard
- [ ] Copy API key
- [ ] Test key with curl:

```bash
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_TAVILY_KEY",
    "query": "Tesla company overview",
    "max_results": 5
  }'
```

**Expected Response:**
```json
{
  "query": "Tesla company overview",
  "results": [
    {
      "title": "Tesla, Inc. - Official Website",
      "url": "https://www.tesla.com",
      "content": "...",
      "score": 0.98
    },
    ...
  ]
}
```

**Cost Check:**
- Free tier: 1,000 searches/month
- Pricing: $0.001 per search after free tier
- Expected usage: ~10-20 searches per research = $0.01-$0.02

### Step 5: Create Environment Configuration

**Goal:** Store API keys securely

**Actions:**
- [ ] Create `.env` file in project root
- [ ] Add API keys:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
TAVILY_API_KEY=tvly-your-key-here

# Optional: Set usage limits for safety
ANTHROPIC_MAX_TOKENS=100000  # Stop if we exceed this in a session
TAVILY_MAX_SEARCHES=100      # Stop if we exceed this in a session
```

- [ ] Create `.env.example` template:

```bash
# .env.example
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
TAVILY_API_KEY=tvly-your-key-here
ANTHROPIC_MAX_TOKENS=100000
TAVILY_MAX_SEARCHES=100
```

- [ ] Add `.env` to `.gitignore`:

```bash
# .gitignore
.env
venv/
__pycache__/
*.pyc
.mypy_cache/
outputs/
```

**Verification:**
```bash
# Make sure .env is ignored
git status  # Should NOT show .env
cat .env    # Should show your actual keys
cat .env.example  # Should show template
```

### Step 6: Install Dependencies

**Goal:** Install required Python packages

**Actions:**
- [ ] Create `requirements.txt`:

```txt
# requirements.txt
anthropic>=0.34.0
tavily-python>=0.5.0
python-dotenv>=1.0.0
pydantic>=2.9.0
aiohttp>=3.10.0
```

- [ ] Install dependencies:

```bash
pip install -r requirements.txt
```

- [ ] Verify installations:

```bash
pip list | grep anthropic
pip list | grep tavily
pip list | grep dotenv
```

**Verification:**
```python
# test_imports.py
import anthropic
import tavily
from dotenv import load_dotenv
import os

load_dotenv()

# Test we can load keys
assert os.getenv("ANTHROPIC_API_KEY"), "Missing ANTHROPIC_API_KEY"
assert os.getenv("TAVILY_API_KEY"), "Missing TAVILY_API_KEY"

# Test we can create clients
anthropic_client = anthropic.Anthropic()
tavily_client = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("✅ All imports successful!")
print("✅ API keys loaded!")
print("✅ Clients created!")
```

Run test:
```bash
python test_imports.py
```

### Step 7: Create Project Structure

**Goal:** Organized directory structure

**Actions:**
- [ ] Create necessary directories:

```bash
mkdir -p src outputs tests
```

- [ ] Verify structure:

```
Lang ai/
├── .env                 # ✅ Your API keys
├── .env.example         # ✅ Template
├── .gitignore          # ✅ Ignore .env
├── requirements.txt     # ✅ Dependencies
├── venv/               # ✅ Virtual environment
├── src/                # ✅ Source code (coming soon)
├── outputs/            # ✅ Generated reports
└── tests/              # ✅ Tests (coming soon)
```

**Verification:**
```bash
ls -la  # Should see all directories
```

## Acceptance Criteria

- [x] Python 3.11+ installed and working
- [x] Virtual environment created and activated
- [x] Anthropic API key obtained and tested
- [x] Tavily API key obtained and tested
- [x] `.env` file created with both keys
- [x] Dependencies installed successfully
- [x] Project directories created
- [x] `test_imports.py` runs without errors
- [x] `.env` is in `.gitignore`

## Testing Instructions

Run all verification steps:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Test Python version
python --version  # Should be 3.11+

# 3. Test imports
python test_imports.py  # Should print success messages

# 4. Verify directory structure
ls -la  # Should see src/, outputs/, tests/, .env, requirements.txt

# 5. Verify .env is ignored
git status  # Should NOT show .env

# All checks should pass! ✅
```

## Success Metrics

- **Setup Time:** < 2 hours (target: 1 hour)
- **Dependencies:** All installed without errors
- **API Access:** Both APIs respond successfully
- **Ready for Development:** Can start writing code immediately

## Common Issues & Solutions

### Issue 1: "Python not found" after installation
**Solution:** Restart terminal/VSCode, check PATH environment variable

### Issue 2: "Permission denied" when creating venv
**Solution:** Run with appropriate permissions, check disk space

### Issue 3: "API key invalid" when testing
**Solution:**
- Make sure you copied the full key
- Check for extra spaces or newlines
- Verify key hasn't been revoked in API dashboard

### Issue 4: "Module not found" after pip install
**Solution:**
- Make sure virtual environment is activated (see `(venv)` in prompt)
- Run `pip install -r requirements.txt` again
- Try `pip install --upgrade pip` first

### Issue 5: Anthropic API returns 429 (rate limit)
**Solution:** You're likely on free tier and hit limits. Wait or upgrade plan.

### Issue 6: Tavily returns empty results
**Solution:**
- Check your query is valid
- Verify API key is correct
- Check Tavily dashboard for usage limits

## Next Steps

After completing this task:
1. Mark status as [x] Complete
2. Update time in Phase 0 README
3. Move to Task 2: [API Integration](02-api-integration.md)
4. Commit your `.env.example` and `requirements.txt` to git:

```bash
git add .env.example requirements.txt .gitignore
git commit -m "feat: setup development environment with API keys"
```

---

**Completed By:** TBD
**Time Spent:** 1.5 hours
**Issues Encountered:** None
**Notes:** Environment setup was straightforward. Both APIs work well.
