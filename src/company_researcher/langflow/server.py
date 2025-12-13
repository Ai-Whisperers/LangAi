"""
LangFlow Server Configuration and Management.

Provides utilities for starting and configuring the LangFlow server
with custom Company Researcher components pre-loaded.

Usage:
    # Start LangFlow with custom components
    from company_researcher.langflow import start_langflow_server
    start_langflow_server(port=7860)

    # Check if LangFlow is available
    from company_researcher.langflow import is_langflow_available
    if is_langflow_available():
        start_langflow_server()
"""

import sys
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from ..utils import get_config, get_logger

logger = get_logger(__name__)

# Check if LangFlow is available
try:
    import langflow
    LANGFLOW_AVAILABLE = True
    LANGFLOW_VERSION = getattr(langflow, "__version__", "unknown")
except ImportError:
    LANGFLOW_AVAILABLE = False
    LANGFLOW_VERSION = None


def is_langflow_available() -> bool:
    """
    Check if LangFlow is installed and available.

    Returns:
        True if LangFlow is installed
    """
    return LANGFLOW_AVAILABLE


def get_langflow_version() -> Optional[str]:
    """
    Get installed LangFlow version.

    Returns:
        Version string or None if not installed
    """
    return LANGFLOW_VERSION


def get_langflow_config(
    port: int = 7860,
    host: str = "127.0.0.1",
    components_path: Optional[str] = None,
    flows_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get LangFlow server configuration.

    Args:
        port: Server port (default: 7860)
        host: Server host (default: localhost)
        components_path: Path to custom components
        flows_path: Path to pre-built flows

    Returns:
        Configuration dictionary for LangFlow
    """
    # Get paths relative to this module
    module_dir = Path(__file__).parent
    default_components_path = module_dir / "components.py"
    default_flows_path = module_dir / "flows"

    config = {
        "host": host,
        "port": port,
        "components_path": components_path or str(default_components_path),
        "flows_path": flows_path or str(default_flows_path),
        "open_browser": True,
        "remove_api_keys": False,
        "cache": "InMemoryCache",
        "dev": False,
        "backend_only": False,
        "store": True,
    }

    # Add environment-based configuration
    if get_config("LANGFLOW_HOST"):
        config["host"] = get_config("LANGFLOW_HOST")
    if get_config("LANGFLOW_PORT"):
        config["port"] = int(get_config("LANGFLOW_PORT"))

    return config


def start_langflow_server(
    port: int = 7860,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    backend_only: bool = False,
    log_level: str = "info",
) -> Optional[subprocess.Popen]:
    """
    Start the LangFlow server with custom components.

    This starts LangFlow with the Company Researcher custom components
    pre-loaded and ready to use in the visual builder.

    Args:
        port: Server port (default: 7860)
        host: Server host (default: localhost)
        open_browser: Open browser automatically
        backend_only: Run backend only (no UI)
        log_level: Logging level

    Returns:
        Subprocess handle or None if failed

    Raises:
        ImportError: If LangFlow is not installed
    """
    if not LANGFLOW_AVAILABLE:
        raise ImportError(
            "LangFlow is not installed. Install with:\n"
            "  pip install langflow\n"
            "Or for full installation:\n"
            "  pip install langflow[all]"
        )

    # Build command
    cmd = [
        sys.executable, "-m", "langflow", "run",
        "--host", host,
        "--port", str(port),
        "--log-level", log_level,
    ]

    if not open_browser:
        cmd.append("--no-open-browser")

    if backend_only:
        cmd.append("--backend-only")

    # Add custom components path
    components_path = Path(__file__).parent / "components.py"
    if components_path.exists():
        cmd.extend(["--components-path", str(components_path)])

    logger.info(f"Starting LangFlow server on {host}:{port}")
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        logger.info(f"LangFlow server started (PID: {process.pid})")
        logger.info(f"Access UI at: http://{host}:{port}")

        return process

    except Exception as e:
        logger.error(f"Failed to start LangFlow server: {e}")
        return None


def start_langflow_dev_server(port: int = 7860) -> Optional[subprocess.Popen]:
    """
    Start LangFlow in development mode with hot reload.

    Args:
        port: Server port

    Returns:
        Subprocess handle
    """
    if not LANGFLOW_AVAILABLE:
        raise ImportError("LangFlow is not installed")

    cmd = [
        sys.executable, "-m", "langflow", "run",
        "--port", str(port),
        "--dev",
        "--log-level", "debug",
    ]

    components_path = Path(__file__).parent / "components.py"
    if components_path.exists():
        cmd.extend(["--components-path", str(components_path)])

    logger.info(f"Starting LangFlow dev server on port {port}")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return process
    except Exception as e:
        logger.error(f"Failed to start dev server: {e}")
        return None


def install_langflow(extras: str = "all") -> bool:
    """
    Install LangFlow if not already installed.

    Args:
        extras: Installation extras ("all", "local", or "")

    Returns:
        True if installation successful
    """
    try:
        package = f"langflow[{extras}]" if extras else "langflow"
        logger.info(f"Installing {package}...")

        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("LangFlow installed successfully")
            return True
        else:
            logger.error(f"Installation failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Installation error: {e}")
        return False


def get_langflow_status() -> Dict[str, Any]:
    """
    Get LangFlow installation and server status.

    Returns:
        Status dictionary with installation and availability info
    """
    status = {
        "installed": LANGFLOW_AVAILABLE,
        "version": LANGFLOW_VERSION,
        "components_available": False,
        "components_path": None,
    }

    if LANGFLOW_AVAILABLE:
        components_path = Path(__file__).parent / "components.py"
        status["components_available"] = components_path.exists()
        status["components_path"] = str(components_path) if components_path.exists() else None

        # List available components
        try:
            from .components import COMPONENT_REGISTRY
            status["components"] = list(COMPONENT_REGISTRY.keys())
        except ImportError:
            status["components"] = []

    return status


def print_langflow_info():
    """Print LangFlow installation and usage information."""
    status = get_langflow_status()

    print("\n" + "=" * 60)
    print("LangFlow Integration Status")
    print("=" * 60)

    if status["installed"]:
        print(f"  Installed: Yes (v{status['version']})")
        print(f"  Components: {len(status.get('components', []))} available")
        if status.get("components"):
            for comp in status["components"]:
                print(f"    - {comp}")
        print(f"\n  Start server with:")
        print(f"    python -c \"from company_researcher.langflow import start_langflow_server; start_langflow_server()\"")
        print(f"\n  Or via CLI:")
        print(f"    langflow run --components-path {status.get('components_path', 'path/to/components.py')}")
    else:
        print("  Installed: No")
        print("\n  Install with:")
        print("    pip install langflow")
        print("  Or:")
        print("    pip install langflow[all]  # Full installation")

    print("=" * 60 + "\n")
