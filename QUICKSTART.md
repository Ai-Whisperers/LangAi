# Quick Start Guide - Get Running in 15 Minutes

**Goal:** Research your first company with AI agents in under 15 minutes!

---

## Prerequisites (5 minutes)

### 1. Python 3.11+
```bash
python --version
# Should show 3.11 or higher
```

### 2. Get API Keys

**Anthropic Claude (Required):**
1. Go to https://console.anthropic.com/
2. Sign up (free $5 credit)
3. Create API key
4. Copy it somewhere safe

**Tavily Search (Required):**
1. Go to https://tavily.com/
2. Sign up (1,000 free searches/month)
3. Get API key
4. Copy it somewhere safe

---

## Installation (5 minutes)

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd "C:/Users/Alejandro/Documents/Ivan/Work/Lang ai"

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 2: Install Dependencies

```bash
# Install Phase 0 minimal dependencies
pip install langgraph langchain langchain-anthropic anthropic tavily-python python-dotenv pydantic aiohttp

# Or install everything:
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed langgraph-... langchain-... anthropic-... tavily-python-...
```

### Step 3: Configure Environment

```bash
# Copy env.example to .env
cp env.example .env

# On Windows, you can also use:
copy env.example .env
```

**Edit .env file:**
```bash
# Open .env in your editor
code .env
# or
notepad .env
```

**Paste your API keys:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-...your-actual-key...
TAVILY_API_KEY=tvly-...your-actual-key...
```

**Save the file!**

---

## Run Your First Research (2 minutes)

### Test with Tesla

```bash
python hello_research.py "Tesla"
```

**Expected output:**
```
============================================================
🔬 Researching: Tesla
============================================================

📡 Step 1: Searching the web...
  🔍 Searching: Tesla company overview
  🔍 Searching: Tesla revenue 2024
  🔍 Searching: Tesla products services
  ✅ Found 9 sources

🤖 Step 2: Analyzing with Claude...
  ✅ Analysis complete

============================================================
📊 RESEARCH RESULTS
============================================================

# Company Overview

Tesla, Inc. is an American electric vehicle and clean energy company
founded in 2003 by Martin Eberhard and Marc Tarpenning, with Elon Musk
joining as chairman in 2004...

## Key Metrics
- Revenue: $96.7B (2023)
- Employees: 127,855
- Founded: 2003
- Market Cap: $789B

## Main Products/Services
- Electric Vehicles (Model S, 3, X, Y, Cybertruck)
- Energy Storage (Powerwall, Megapack)
- Solar Panels and Solar Roof
- Full Self-Driving (FSD) Software

## Key Insights
- Leading EV manufacturer globally with 19.9% market share
- Vertically integrated business model...

============================================================
📈 METRICS
============================================================
⏱️  Duration: 12.3 seconds
💰 Cost: $0.0342
🔢 Tokens: 2,847 in, 412 out
📚 Sources: 9
============================================================

🔗 TOP SOURCES
============================================================
1. Tesla Q4 2023 Earnings Report
   https://ir.tesla.com/...
   Relevance: 98%

...

============================================================
✅ SUCCESS CRITERIA CHECK
============================================================
✅ Duration < 5 minutes
✅ Cost < $0.50
✅ Found sources
✅ Generated summary

🎉 ALL CRITERIA PASSED! Phase 0 successful!
============================================================
```

---

## Try More Companies

```bash
# Research OpenAI
python hello_research.py "OpenAI"

# Research Stripe
python hello_research.py "Stripe"

# Research any company
python hello_research.py "Company Name"
```

---

## Troubleshooting

### Error: "Missing ANTHROPIC_API_KEY"
→ You didn't set up .env file correctly
→ Solution: Make sure you copied env.example to .env and added your keys

### Error: "ModuleNotFoundError: No module named 'anthropic'"
→ Dependencies not installed
→ Solution: `pip install -r requirements.txt`

### Error: "Invalid API key"
→ Wrong API key or typo
→ Solution: Double-check your API keys in .env

### Research takes forever
→ Network issues or API rate limiting
→ Solution: Check your internet connection, wait a minute and retry

### Cost seems high (> $0.50)
→ Company has lots of search results
→ Normal: Phase 0 is unoptimized. Phase 1+ will add caching and optimization

---

## What You Just Did

✅ Set up a complete Python environment
✅ Installed AI agent framework (LangGraph)
✅ Connected to Claude 3.5 Sonnet (best reasoning model)
✅ Connected to Tavily (AI-optimized search)
✅ Researched a company automatically
✅ Got results in < 30 seconds
✅ Spent < $0.05

**This is the foundation of the entire system!**

---

## Next Steps

### Option 1: Keep Testing (Recommended)
```bash
# Test with 5-10 different companies
# Public companies: Tesla, Microsoft, Apple, Google
# Private companies: OpenAI, Stripe, Anthropic
# Small companies: Your local businesses
```

### Option 2: Understand the Code
1. Open `hello_research.py`
2. Read through it (well-commented)
3. See how search + Claude work together

### Option 3: Move to Phase 1
1. Read [MVP_ROADMAP.md](MVP_ROADMAP.md) - Phase 1
2. Start building the LangGraph workflow
3. Add quality reflection loop

---

## Cost Tracking

**Phase 0 typical costs:**
- Per research: $0.02 - $0.05
- 10 companies: ~$0.30
- 100 companies: ~$3.00

**Your free credits:**
- Anthropic: $5 (100+ researches)
- Tavily: 1,000 searches (300+ researches)

**You have plenty to experiment!**

---

## What's Next in the Project

**Week 1 (Phase 1):**
- Build proper LangGraph workflow
- Add state management
- Generate markdown reports
- Add error handling

**Week 2 (Phase 2):**
- Add quality reflection loop
- Improve source verification
- Optimize prompts

**Week 3 (Phase 3):**
- Add 3 specialist agents
- Implement supervisor pattern
- Parallel agent execution

**See [MVP_ROADMAP.md](MVP_ROADMAP.md) for complete plan!**

---

## Common Questions

**Q: Is this the final product?**
A: No, this is Phase 0 - a prototype to validate the concept. The final system will have 14 specialized agents, memory, quality assurance, and much more.

**Q: Can I use this for real research?**
A: Yes! The results are already useful. But always verify critical facts from the sources provided.

**Q: How accurate is it?**
A: Claude 3.5 Sonnet is very accurate, but always check the sources. Phase 2+ will add automatic fact verification.

**Q: Can I research private companies?**
A: Yes! Try: `python hello_research.py "OpenAI"` or `python hello_research.py "Stripe"`

**Q: What if I run out of free credits?**
A: Anthropic charges ~$3 per 1M input tokens, $15 per 1M output tokens. At ~$0.03 per research, $5 gets you 150+ researches. Very affordable!

---

## Success Checklist

- [x] Python 3.11+ installed
- [x] Virtual environment created
- [x] Dependencies installed
- [x] API keys obtained
- [x] .env file configured
- [x] Researched Tesla successfully
- [x] Saw results in < 30 seconds
- [x] Cost was < $0.50
- [ ] Tried 3+ different companies
- [ ] Understand how it works
- [ ] Ready for Phase 1

---

## 🎉 Congratulations!

You just built and ran an AI-powered company research system!

**What you accomplished:**
- Set up professional Python development environment
- Integrated with state-of-the-art AI (Claude 3.5 Sonnet)
- Built a working research automation
- Validated the concept

**You're ready to build the full system!**

→ **Next: Read [MVP_ROADMAP.md](MVP_ROADMAP.md) Phase 1** ←

---

**Questions?** Check [START_HERE.md](START_HERE.md) for comprehensive documentation.

**Stuck?** Review the troubleshooting section above or check your API keys.

**Excited?** Start Phase 1 and build the real multi-agent system! 🚀
