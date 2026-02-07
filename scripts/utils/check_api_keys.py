#!/usr/bin/env python
"""Check which API keys are configured in .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root explicitly
project_root = Path(__file__).parent
env_path = project_root / ".env"
print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    print("[ERROR] .env file not found!")

# Define expected API keys with alternates
API_KEYS = {
    # REQUIRED
    "ANTHROPIC_API_KEY": {"required": True, "prefix": "sk-ant-", "desc": "Claude LLM", "alts": []},
    "TAVILY_API_KEY": {"required": True, "prefix": "tvly-", "desc": "Web Search", "alts": []},
    # LLM Providers
    "GOOGLE_API_KEY": {
        "required": False,
        "prefix": "",
        "desc": "Gemini",
        "alts": ["GEMINI_API_KEY"],
    },
    "GROQ_API_KEY": {"required": False, "prefix": "gsk_", "desc": "Groq", "alts": []},
    "OPENAI_API_KEY": {"required": False, "prefix": "sk-", "desc": "OpenAI", "alts": []},
    # Search Providers
    "SERPER_API_KEY": {"required": False, "prefix": "", "desc": "Serper", "alts": []},
    "BRAVE_API_KEY": {"required": False, "prefix": "", "desc": "Brave", "alts": []},
    "JINA_API_KEY": {"required": False, "prefix": "", "desc": "Jina", "alts": []},
    "LANGSEARCH_API_KEY": {"required": False, "prefix": "", "desc": "LangSearch", "alts": []},
    # Financial APIs
    "ALPHA_VANTAGE_API_KEY": {"required": False, "prefix": "", "desc": "Alpha Vantage", "alts": []},
    "FMP_API_KEY": {
        "required": False,
        "prefix": "",
        "desc": "Financial Modeling",
        "alts": ["FINANCIAL_MODELING_PREP_API_KEY"],
    },
    # News APIs
    "NEWSAPI_KEY": {"required": False, "prefix": "", "desc": "NewsAPI", "alts": []},
    # Other
    "GITHUB_TOKEN": {
        "required": False,
        "prefix": "",
        "desc": "GitHub",
        "alts": ["GITHUB_API_TOKEN"],
    },
}


def check_key(key_name, config):
    """Check if a key is configured and valid."""
    # Check primary key name first
    value = os.getenv(key_name, "")

    # Check alternate names if primary not set
    if not value and config.get("alts"):
        for alt in config["alts"]:
            value = os.getenv(alt, "")
            if value:
                key_name = f"{key_name} (via {alt})"
                break

    if not value or value.endswith("-your-key-here") or value == "your-key-here":
        return "NOT SET", "[X]"

    # Check prefix if specified
    prefix = config.get("prefix", "")
    if prefix and not value.startswith(prefix):
        return f"INVALID FORMAT (expected {prefix}...)", "[!]"

    # Mask the value
    masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
    return f"SET ({masked})", "[OK]"


print("=" * 70)
print("API KEY CONFIGURATION CHECK")
print("=" * 70)

# Check required keys first
print("\nREQUIRED KEYS (for automated research):")
print("-" * 50)
for key, config in API_KEYS.items():
    if config["required"]:
        status, icon = check_key(key, config)
        print(f"  {icon} {key:<25} {status}")

# Check optional keys
print("\nOPTIONAL KEYS (for enhanced features):")
print("-" * 50)
for key, config in API_KEYS.items():
    if not config["required"]:
        status, icon = check_key(key, config)
        desc = config["desc"]
        print(f"  {icon} {key:<25} [{desc}] {status}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

required_ok = all(check_key(k, c)[1] == "[OK]" for k, c in API_KEYS.items() if c["required"])

if required_ok:
    print("[OK] All required keys are configured! Automated research should work.")
else:
    print("[X] Some required keys are missing or invalid.")
    print("\nTo fix:")
    print("1. Get Anthropic key at: https://console.anthropic.com/")
    print("2. Get Tavily key at: https://tavily.com/ (free tier: 1000 queries/month)")
    print("3. Update your .env file with valid keys")

# Count configured optional keys
optional_count = sum(
    1 for k, c in API_KEYS.items() if not c["required"] and check_key(k, c)[1] == "[OK]"
)
print(
    f"\nOptional keys configured: {optional_count}/{len([k for k,c in API_KEYS.items() if not c['required']])}"
)
