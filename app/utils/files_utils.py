import logging
from pathlib import Path
from datetime import datetime

from app.config.config_paths import OUTPUT_DIR


logger = logging.getLogger(__name__)


def get_default_output_path() -> Path:
    """
    Returns the default output path for the app
    """
    logger.debug("Getting default output path")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"PaleobiodbDataset_{timestamp}.csv"
    return OUTPUT_DIR.joinpath(filename)


def ensure_output_dir(output_dir: Path) -> Path:
    """
    Ensures that the output directory exists.

    :param output_dir: Path to the output directory.
    """
    logger.debug(f"Ensuring output directory exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
