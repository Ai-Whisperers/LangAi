#!/usr/bin/env python3
"""
{{SCRIPT_NAME}}

{{SCRIPT_DESCRIPTION}}

This script supports both local execution and CI/CD environments.
Configuration can be provided via command-line arguments or external YAML config file.

Features:
    - Comprehensive CLI with argparse
    - Type hints and Pydantic validation
    - Structured logging with levels
    - Portable (works locally and in CI/CD)
    - Configuration file support (YAML)
    - Proper exit codes

Usage:
    Basic usage with defaults:
        $ python {{SCRIPT_NAME}}.py

    Custom configuration:
        $ python {{SCRIPT_NAME}}.py --config Release --output /tmp/output

    With config file:
        $ python {{SCRIPT_NAME}}.py --config-file config.yaml

    Show help:
        $ python {{SCRIPT_NAME}}.py --help

Examples:
    Run with default settings:
        $ python {{SCRIPT_NAME}}.py

    Run with custom parameters:
        $ python {{SCRIPT_NAME}}.py --{{PARAMETER_NAME}} {{PARAMETER_VALUE}}

    Run in Azure Pipelines:
        - task: PythonScript@0
          inputs:
            scriptPath: 'scripts/{{SCRIPT_NAME}}.py'
            arguments: '--{{PARAMETER_NAME}} {{PARAMETER_VALUE}}'

Requirements:
    - Python 3.9+
    - {{ADDITIONAL_REQUIREMENTS}}

Author:
    {{AUTHOR}}

Version:
    1.0.0

Quality Level:
    Standard (Production-Ready)
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    from pydantic import BaseModel, Field, validator
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install pyyaml pydantic")
    sys.exit(2)

__version__ = "1.0.0"
__author__ = "{{AUTHOR}}"


# ======================================
# Configuration Models (Pydantic)
# ======================================

class ScriptConfig(BaseModel):
    """Configuration model with validation."""

    configuration: str = Field(default="Release", pattern="^(Debug|Release)$")
    output_path: Optional[Path] = None
    {{PARAMETER_NAME}}: int = Field(default={{DEFAULT_VALUE}}, ge={{MIN_VALUE}}, le={{MAX_VALUE}})
    enable_feature: bool = Field(default=False)
    excluded_items: list[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True
        extra = "forbid"

    @validator('output_path', pre=True, always=True)
    def set_output_path(cls, v, values):
        """Set portable default for output path."""
        if v is not None:
            return Path(v)

        # Detect environment
        if os.getenv('AGENT_TEMPDIRECTORY'):
            # Azure Pipelines
            return Path(os.getenv('BUILD_ARTIFACTSTAGINGDIRECTORY', '/tmp')) / '{{SCRIPT_NAME}}'
        else:
            # Local
            return Path.home() / 'tmp' / '{{SCRIPT_NAME}}'


# ======================================
# Logging Setup
# ======================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure structured logging with console handler.

    Args:
        verbose: Enable debug logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('{{SCRIPT_NAME}}')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Format: [2025-12-07 14:30:15] [INFO] Message
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Azure Pipelines integration
    if os.getenv('AGENT_TEMPDIRECTORY'):
        azure_handler = AzurePipelinesHandler()
        logger.addHandler(azure_handler)

    return logger


class AzurePipelinesHandler(logging.Handler):
    """Custom handler for Azure Pipelines logging commands."""

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            print(f"##vso[task.logissue type=error]{record.getMessage()}")
        elif record.levelno >= logging.WARNING:
            print(f"##vso[task.logissue type=warning]{record.getMessage()}")


# ======================================
# Configuration Loading
# ======================================

def load_config_file(config_file: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)

    return config_data or {}


# ======================================
# Main Processing Logic
# ======================================

def process(config: ScriptConfig, logger: logging.Logger) -> Dict[str, Any]:
    """
    Main processing logic.

    Args:
        config: Validated configuration
        logger: Logger instance

    Returns:
        Dictionary with results

    Raises:
        RuntimeError: If processing fails
    """
    logger.info("Starting processing...")

    # Create output directory
    config.output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {config.output_path}")

    # ======================================
    # TODO: Replace with actual logic
    # ======================================

    logger.info(f"Configuration: {config.configuration}")
    logger.info(f"{{PARAMETER_NAME}}: {config.{{PARAMETER_NAME}}}")

    # Example: Process items
    results = {
        'timestamp': datetime.now().isoformat(),
        'configuration': config.configuration,
        '{{PARAMETER_NAME}}': config.{{PARAMETER_NAME}},
        'status': 'success',
        # TODO: Add actual result data
    }

    logger.info("Processing complete")

    return results


# ======================================
# CLI Argument Parser
# ======================================

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='{{SCRIPT_DESCRIPTION}}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --config Debug --output /tmp/output
  %(prog)s --config-file config.yaml
        """
    )

    parser.add_argument(
        '--config',
        choices=['Debug', 'Release'],
        default='Release',
        help='Build configuration (default: Release)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output directory path'
    )

    parser.add_argument(
        '--config-file',
        type=Path,
        default=Path(__file__).parent / '{{SCRIPT_NAME}}-config.yaml',
        help='Path to YAML configuration file'
    )

    parser.add_argument(
        '--{{PARAMETER_NAME}}',
        type=int,
        default={{DEFAULT_VALUE}},
        help='{{PARAMETER_DESCRIPTION}} (default: {{DEFAULT_VALUE}})'
    )

    parser.add_argument(
        '--enable-feature',
        action='store_true',
        help='Enable optional feature'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    return parser.parse_args()


# ======================================
# Main Entry Point
# ======================================

def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    # Parse arguments
    args = parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose)

    logger.info("=" * 50)
    logger.info("{{SCRIPT_NAME}}")
    logger.info("=" * 50)

    try:
        # Load config file if exists
        config_dict = {}
        if args.config_file.exists():
            logger.info(f"Loading configuration from: {args.config_file}")
            config_dict = load_config_file(args.config_file)
        else:
            logger.info("No config file found, using command-line arguments")

        # Override with command-line arguments
        if args.config:
            config_dict['configuration'] = args.config
        if args.output:
            config_dict['output_path'] = args.output
        if args.{{PARAMETER_NAME}}:
            config_dict['{{PARAMETER_NAME}}'] = args.{{PARAMETER_NAME}}
        if args.enable_feature:
            config_dict['enable_feature'] = args.enable_feature

        # Validate configuration with Pydantic
        config = ScriptConfig(**config_dict)

        logger.info(f"Configuration: {config.configuration}")
        logger.info(f"Output Path: {config.output_path}")
        logger.info(f"{{PARAMETER_NAME}}: {config.{{PARAMETER_NAME}}}")
        logger.info("")

        # Process
        results = process(config, logger)

        # Save results
        results_file = config.output_path / 'results.json'
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("")
        logger.info("✅ Script completed successfully!")
        logger.info(f"Output saved to: {config.output_path}")
        logger.info("")

        return 0

    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        logger.debug("Stack trace:", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
