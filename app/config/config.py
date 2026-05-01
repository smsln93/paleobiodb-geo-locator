import tomllib
import logging
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

from .config_paths import APP_CONFIG_FILE

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """
    Raised when configuration is missing or invalid.
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

        self._load_app_config()
        self._assign_app_parameters()

        if self.env_config_path is not None:
            self._load_env_config()
            self._assign_env_parameters()

    def _load_app_config(self) -> None:
        """
        Loads configuration variables from the provided TOML file path.

        :raises ConfigError: If configuration cannot be loaded or is invalid.
        """
        logger.debug(f"Loading configuration from {self.app_config_path} file...")
        try:
            with self.app_config_path.open('rb') as app_config:
                self.cfg_params = tomllib.load(app_config)

        except FileNotFoundError as file_not_found_err:
            raise ConfigError(f"Missing configuration file: {self.app_config_path}"
                              f"Ensure it exists in the \\config directory.") from file_not_found_err
        except tomllib.TOMLDecodeError as toml_error:
            raise ConfigError(f"Invalid TOML configuration: {self.app_config_path}.") from toml_error
        else:
            logger.debug(f"Configuration from {self.app_config_path} file has been properly loaded")

    def _load_env_config(self) -> None:
        """
        Loads environment variables from .env file.

        :raises ConfigError: If configuration cannot be loaded or is invalid.
        """
        logger.debug("Loading configuration from .env file...")

        if self.env_config_path and not self.env_config_path.exists():
            raise ConfigError(".env file not found")

        self.env_variables = dotenv_values(self.env_config_path)
        if not self.env_variables:
            raise ConfigError(".env file is empty")

        logger.debug("Configuration from .env file has been properly loaded")

    def _assign_app_parameters(self) -> None:
        """
        Assigns application configuration parameters.
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

        except KeyError as key_err:
            raise ConfigError("Missing configuration key") from key_err
        else:
            logger.debug("Application configuration parameters assigned successfully")

    def _assign_env_parameters(self) -> None:
        """
        Assigns environment configuration parameters.
        """
        try:
            self.email_host = self.env_variables["EMAIL_HOST"]
            self.email_login = self.env_variables["EMAIL_LOGIN"]
            self.email_from = self.env_variables["EMAIL_FROM"]
            self.email_password = self.env_variables["EMAIL_PASSWORD"]

            if not all([
                self.email_host,
                self.email_login,
                self.email_from,
                self.email_password
            ]):
                raise ConfigError("Email configuration contains empty required fields")

            port = self.env_variables["EMAIL_PORT"]
            if not port or port.strip() == "":
                raise ConfigError("Email port cannot be empty")

            try:
                self.email_port = int(port)
            except ValueError as value_error:
                raise ConfigError(f"Invalid email_port value: {port}") from value_error

            email_to = self.env_variables["EMAIL_TO"]
            if not email_to or not email_to.strip():
                self.email_to = []
            else:
                self.email_to = [email.strip() for email in email_to.split(",") if email.strip()]

        except KeyError as key_err:
            raise ConfigError(f"Missing configuration key") from key_err
        else:
            logger.debug("Environment configuration parameters assigned successfully")
