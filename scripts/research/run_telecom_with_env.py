#!/usr/bin/env python3
"""
Wrapper script that loads .env before running telecom research.
This ensures API keys are loaded before any config singleton is created.
"""
import os
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env FIRST - BEFORE any other project imports
from dotenv import load_dotenv

env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"[OK] Loaded environment from: {env_path}")

    # Verify keys loaded
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if key:
        print(f"[OK] ANTHROPIC_API_KEY: {key[:15]}...{key[-10:]}")
    else:
        print("[ERROR] ANTHROPIC_API_KEY not loaded!")
        sys.exit(1)
else:
    print(f"[ERROR] .env file not found at: {env_path}")
    sys.exit(1)

# Now we can import the rest
# Force config to be created AFTER env vars are loaded
from src.company_researcher import config as config_module

# Clear any cached config
config_module._config = None

if __name__ == "__main__":
    # Pass through all command line args to main script
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_all_telecom_research", project_root / "run_all_telecom_research.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_all_telecom_research"] = module
    spec.loader.exec_module(module)

    # Call main
    sys.exit(module.main())
