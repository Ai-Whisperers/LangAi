#!/usr/bin/env python
"""Update .env file with actual API keys."""
from pathlib import Path
import re

# Keys to update (from user's other project)
KEYS_TO_UPDATE = {
    # Core APIs - REQUIRED
    "ANTHROPIC_API_KEY": "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",
    "TAVILY_API_KEY": "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",  # User's preferred key

    # Search Providers
    "SERPER_API_KEY": "ee48cdc2999c513e56bc3199a2383eab8dadab33",  # User's preferred key
    "BRAVE_API_KEY": "BSAze4mICDeFLTiQ7Vqu18v-Hg28UKl",

    # LLM Providers
    "OPENAI_API_KEY": "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",
    "GOOGLE_API_KEY": "AIzaSyDScOadQFTp3ZjNTEQCoY-3feA0FZz-fTY",
    "GROQ_API_KEY": "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",

    # Financial APIs
    "ALPHA_VANTAGE_API_KEY": "STUK2IO01XL36C8X",
    "FMP_API_KEY": "5snFFS1J2kwmtzwm39mYYRzQdvXBvFL5",

    # News APIs
    "NEWSAPI_KEY": "c7686d9e322d406f88eee8692e1da46b",

    # Developer APIs
    "GITHUB_TOKEN": "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",

    # Observability
    "LANGFUSE_PUBLIC_KEY": "pk-lf-796b9234-2405-46e2-9ba3-29c52d3ccf0d",
    "LANGFUSE_SECRET_KEY": "sk-lf-da4f9198-989f-4b92-888c-4029ecc82b02",
    "LANGFUSE_ENABLED": "true",
    "LANGCHAIN_API_KEY": "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",
}

def update_env():
    env_path = Path(".env")

    if not env_path.exists():
        print("[ERROR] .env file not found!")
        return

    content = env_path.read_text()
    updated = 0

    for key, value in KEYS_TO_UPDATE.items():
        # Pattern to match the key with any value (including empty)
        pattern = rf'^{re.escape(key)}=.*$'
        replacement = f'{key}={value}'

        if re.search(pattern, content, re.MULTILINE):
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                print(f"[UPDATED] {key}")
                updated += 1
            else:
                print(f"[UNCHANGED] {key} (already has correct value)")
        else:
            # Key not found, append it
            content += f"\n{key}={value}"
            print(f"[ADDED] {key}")
            updated += 1

    # Write back
    env_path.write_text(content)
    print(f"\n[DONE] Updated {updated} keys in .env")

if __name__ == "__main__":
    print("=" * 60)
    print("Updating .env with API keys...")
    print("=" * 60)
    update_env()
    print("\nRun 'python check_api_keys.py' to verify.")
