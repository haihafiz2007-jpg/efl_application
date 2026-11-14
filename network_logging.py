"""Local logging for failures from external network services."""
from pathlib import Path

import config


def log_network_failure(error):
    """Append rate-provider failures to the configured local log file."""
    log_dir = Path(config.LOG_DIR)
    if not log_dir.is_absolute():
        log_dir = Path(__file__).parent / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "network.log").open("a", encoding="utf-8") as log_file:
        log_file.write(f"Rate refresh failed: {type(error).__name__}: {error}\n")
