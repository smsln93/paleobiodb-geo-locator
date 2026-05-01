import argparse
import sys
from pathlib import Path
from typing import Tuple

from app.utils.logging_utils import setup_logger
from app.config.config import Config, ConfigError
from app.utils.files_utils import get_default_output_path, ensure_output_dir
from app.services.paleobiodb_dataset import PaleobiodbDataset, DatasetWriteError, DatasetReadError
from app.services.paleobiodb_email_sender import PaleobiodbEmailSender, EmailSendError
from app.utils.requests_utils import DataFetchError


DESCRIPTION = """
Fetch records from Paleobiology Database and send an email report with a CSV file of occurrences.

Data can be fetched directly from the PaleobioDB API or loaded from a CSV file.

Options:
  --csv FILE
      Load records from a CSV file instead of calling the API.

  --interval NAME
      Geological time interval (e.g., 'Callovian').

  --boundary-box MIN_LATITUDE MIN_LONGITUDE MAX_LATITUDE MAX_LONGITUDE
           Geographic bounding box as floats: min latitude, min longitude, max latitude, max longitude.

  --output PATH
      Optional path to the output CSV file. 

  --limit N
      Limit number of records.

  --filter-species
      Include only species-level records (rank = 5).

  --filter-group NAME
      Filter by phylogenetic group (e.g., 'Dinosauria').

  --filter-class NAME
      Filter by taxonomic class (e.g., 'Anthozoa').

  --send-email
      Send the email report.

Examples:
  python main.py --interval Maastrichtian \
    --min-longitude -105 --max-longitude -102 \
    --min-latitude 46 --max-latitude 48 \
    --limit 100 --filter-group Dinosauria
    
  python main.py --csv configs.csv \
    --interval Callovian \
    --min-longitude 10 --max-longitude 20 \
    --min-latitude 40 --max-latitude 50 --send-email
"""


def send_report_email(config: Config, dataset: PaleobiodbDataset,  file: Path) -> None:

    email_sender = PaleobiodbEmailSender(
        host=config.email_host,
        login=config.email_login,
        mail_from=config.email_from,
        password=config.email_password,
        port=config.email_port,
        mail_to=config.email_to
    )

    email_sender.send_email_report(
        subject=f"PaleobioDB Report for {config.interval}",
        dataset=dataset,
        data_file=file
    )


def validate_boundary_box(min_latitude: float, min_longitude: float, max_latitude: float, max_longitude: float) \
        -> Tuple[float, float, float, float]:

    if not -90 <= min_latitude <= 90:
        raise argparse.ArgumentTypeError("Minimum latitude must be between -90 and 90.")

    if not -90 <= max_latitude <= 90:
        raise argparse.ArgumentTypeError("Maximum latitude must be between -90 and 90.")

    if not -180 <= min_longitude <= 180:
        raise argparse.ArgumentTypeError("Minimum longitude must be between -180 and 180.")

    if not -180 <= max_longitude <= 180:
        raise argparse.ArgumentTypeError("Maximum longitude must be between -180 and 180.")

    if min_latitude > max_latitude:
        raise argparse.ArgumentTypeError("Minimum latitude must be less than maximum latitude.")

    if min_longitude > max_longitude:
        raise argparse.ArgumentTypeError("Minimum longitude must be less than maximum longitude.")

    return min_latitude, min_longitude, max_latitude, max_longitude


def csv_path(value: str) -> Path:
    path = Path(value)
    if path.suffix.lower() != ".csv":
        raise argparse.ArgumentTypeError("File must have .csv extension")
    return path


def main():
    parser = argparse.ArgumentParser(prog="Paleobiodb-geo-reporter",
                                     description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--input-csv",
                        help="Path to CSV file instead of fetching from API.",
                        default=None)

    parser.add_argument("--interval",
                        help="Named unit of geological time.",
                        type=str)

    parser.add_argument("--boundary-box",
                        help="Search area as: min_latitude, min_longitude, max_latitude, max_longitude",
                        nargs=4,
                        type=float,
                        metavar=("min_latitude", "min_longitude", "max_latitude", "max_longitude"),
                        required=False)

    parser.add_argument("--output-csv",
                        help="Path to the CSV file to save the results.",
                        type=csv_path,
                        required=False)

    parser.add_argument("--limit",
                        help="Maximum number of records to be fetched.",
                        type=int,
                        default=None)

    parser.add_argument("--filter-species",
                        help="Filter by the taxonomic level of species.",
                        type=str,
                        default=None)

    parser.add_argument("--filter-group",
                        help="Filter by phylogenetic group.",
                        type=str,
                        default=None)

    parser.add_argument("--filter-class",
                        help="Filter by the taxonomic rank of Class.",
                        type=str,
                        default=None)

    parser.add_argument("--send-email",
                        help="Send email report",
                        action="store_true",
                        required=False)

    parser.add_argument("--log-to-file",
                        help="Enable logging to a file.",
                        action="store_true",
                        required=False)

    parser.add_argument("--debug",
                        help="Enable additional DEBUG level logs.",
                        action="store_true",
                        required=False)

    arguments = parser.parse_args()

    logger = setup_logger(log_to_file=arguments.log_to_file, debug=arguments.debug)

    logger.info("Starting PaleobioDB CLI")

    try:
        config = Config()
    except ConfigError as cfg_err:
        logger.error(f"Config failed: {cfg_err}")
        sys.exit(1)

    if arguments.boundary_box is not None:
        min_latitude, min_longitude, max_latitude, max_longitude = arguments.boundary_box
    else:
        min_latitude = config.min_latitude
        min_longitude = config.min_longitude
        max_latitude = config.max_latitude
        max_longitude = config.max_longitude

    validate_boundary_box(min_latitude, min_longitude, max_latitude, max_longitude)
    logger.debug(f"Resolved bounding box: {min_latitude, min_longitude, max_latitude, max_longitude}")

    logger.info("Building dataset...")
    try:
        if arguments.input_csv:
            dataset = PaleobiodbDataset.from_csv(arguments.input_csv)
        else:
            dataset = PaleobiodbDataset.from_api(
                base_url=config.base_url,
                geological_period=config.interval,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude,
                query_parameters=config.query_parameters
            )
    except (DatasetReadError, DataFetchError) as dataset_build_err:
        logger.error(f"Dataset build failed: {dataset_build_err}")
        sys.exit(1)

    if arguments.filter_species is not None:
        records = dataset.filter_species()
        dataset = PaleobiodbDataset(records)

    if arguments.filter_group is not None:
        records = dataset.filter_by_phylogenetic_group(arguments.filter_group)
        dataset = PaleobiodbDataset(records)

    if arguments.filter_class is not None:
        records = dataset.filter_by_class(arguments.filter_class)
        dataset = PaleobiodbDataset(records)

    if arguments.limit is not None:
        dataset = PaleobiodbDataset(dataset.limit(arguments.limit))

    logger.info("Saving results to CSV file...")
    output_file = arguments.output_csv or get_default_output_path()
    ensure_output_dir(output_file.parent)

    try:
        dataset.to_csv(output_file)
    except DatasetWriteError as write_err:
        logger.error(f"Dataset write failed: {write_err}")
        sys.exit(1)

    send_email_flag = arguments.send_email or config.send_email

    if send_email_flag:
        try:
            send_report_email(config, dataset, output_file)
        except EmailSendError as email_send_err:
            logger.warning(f"Email sending failed: {email_send_err}")


if __name__ == "__main__":
    main()
