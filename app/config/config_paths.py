from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
APP_DIR = PROJECT_ROOT.joinpath("app")
APP_CONFIG_DIR = APP_DIR.joinpath("config")
APP_CONFIG_FILE = APP_CONFIG_DIR.joinpath("config.toml")
OUTPUT_DIR = PROJECT_ROOT.joinpath("output")
LOG_DIR = PROJECT_ROOT.joinpath("logs")
DATA_DIR = PROJECT_ROOT.joinpath("data")
ENV_FILE = PROJECT_ROOT.joinpath(".env")