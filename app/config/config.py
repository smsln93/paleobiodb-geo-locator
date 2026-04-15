import tomllib
import logging
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

from .config_paths import APP_CONFIG_FILE

logger = logging.getLogger(__name__)


class DotEnvNotFoundException(Exception):
    """
    Raised when .env file cannot be loaded.
    """
    pass


class Config:
    """
    Loads environment variables from the .env file, reads configuration from config.toml,
    and assigns all required parameters.

    Attributes:
        app_config_path (Path): Path to the TOML configuration file.
        env_config_path (Path): Path to the .env file.
    """
    def __init__(self, app_config_path: Path = APP_CONFIG_FILE, env_config_path: Optional[Path] = None):
        self.app_config_path = app_config_path
        self.env_config_path = env_config_path

        self._load_toml()
        if self.env_config_path is not None:
            self._load_env()

        self._assign_parameters()

    def _load_toml(self) -> None:
        """
        Loads configuration variables from the provided TOML file path.

        :raises FileNotFoundError: If TOML file does not exist in config directory.
        :raises tomllib.TOMLDecodeError: If TOML file cannot be properly decoded.
        """
        logger.debug(f"Loading configuration from {self.app_config_path} file...")
        try:
            with self.app_config_path.open('rb') as app_config:
                self.cfg_params = tomllib.load(app_config)

        except FileNotFoundError:
            logger.error(f"{self.app_config_path} file not found. "
                           f"Make sure the file exists in the \\config directory.")
            raise
        except tomllib.TOMLDecodeError as decode_exc:
            logger.error(f"Failed to decode {self.app_config_path} file: {decode_exc}")
            raise
        else:
            logger.debug(f"Configuration from {self.app_config_path} file has been properly loaded")

    def _load_env(self) -> None:
        """
        Loads environment variables from .env file.

        :raises DotEnvNotFoundException: If .env file cannot be found or required keys are missing.
        """
        logger.debug("Loading configuration from .env file...")
        try:

            env_file_variables = dotenv_values(self.env_config_path)
            if env_file_variables is None:
                raise DotEnvNotFoundException(".env file not found")

            if len(env_file_variables) == 0:
                raise DotEnvNotFoundException(".env file is empty")

            self.env_variables = dict(env_file_variables or {})

        except DotEnvNotFoundException as dotenv_exc:
            logger.error(f"Failed to load environment variables from .env file: {dotenv_exc}")
            raise
        else:
            logger.debug("Configuration from .env file has been properly loaded")

    def _assign_parameters(self) -> None:
        """
        Assigns configuration parameters.
        """
        try:
            self.base_url = self.cfg_params["paleobiodb"]["base_url"]
            self.interval = self.cfg_params["paleobiodb"]["interval"]
            self.send_email = self.cfg_params["application"]["send_email"]
            self.query_parameters = self.cfg_params["application"]["query_parameters"]
            self.min_longitude = self.cfg_params["geospatial"]["min_longitude"]
            self.min_latitude = self.cfg_params["geospatial"]["min_latitude"]
            self.max_longitude = self.cfg_params["geospatial"]["max_longitude"]
            self.max_latitude = self.cfg_params["geospatial"]["max_latitude"]

            self.email_host = self.env_variables["EMAIL_HOST"]
            self.email_login = self.env_variables["EMAIL_LOGIN"]
            self.email_from = self.env_variables["EMAIL_FROM"]
            self.email_password = self.env_variables["EMAIL_PASSWORD"]

            port = self.env_variables["EMAIL_PORT"]
            if port is None or port == "":
                raise ValueError("Email port cannot be empty")

            self.email_port = int(port)

            email_to = self.env_variables["EMAIL_TO"]

            if email_to is None or email_to.strip() == "":
                self.email_to = []
            else:
                self.email_to = [email.strip() for email in email_to.split(",") if email.strip()]

        except KeyError as key_err:
            logger.error(f"Missing key in config.toml: {key_err}")
        else:
            logger.debug("Configuration parameters assigned successfully")
