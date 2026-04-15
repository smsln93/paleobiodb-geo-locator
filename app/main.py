import argparse
from pathlib import Path
from typing import Tuple

from app.utils.logging_utils import setup_logger
from app.config.config import Config
from app.utils.requests_utils import fetch_paleobiodb_content
from app.services.paleobiodb_dataset import PaleobiodbDataset
from app.services.paleobiodb_email_sender import PaleobiodbEmailSender


DESCRIPTION = """
Fetch PaleobioDB records and optionally send an HTML report by email.

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
      Send the HTML report via email.

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


def send_report_email(dataset, config):
    html_table = dataset.create_table_html()

    email_sender = PaleobiodbEmailSender(
        host=config.email_host,
        login=config.email_login,
        mail_from=config.email_from,
        password=config.email_password,
        port=config.email_port,
        mail_to=config.email_to
    )

    email_sender.send_html_report(
        subject=f"PaleobioDB Report for {config.interval}",
        title="PaleobioDB Data Report",
        html_table=html_table
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
                        type=str,
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
                        help="Send HTML report by email",
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

    config = Config()

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
    if arguments.input_csv is not None:
        dataset = PaleobiodbDataset.from_csv(Path(arguments.input_csv))
    else:
        logger.info("Fetching configs from API...")
        records = fetch_paleobiodb_content(
            base_url=config.base_url,
            geological_period=config.interval,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            show=config.show
        )
        dataset = PaleobiodbDataset(records)

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
    if arguments.output_csv:
        dataset.to_csv(arguments.output_csv)
    else:
        dataset.to_csv()

    send_email_flag = arguments.send_email or config.send_email


    if send_email_flag:
        send_report_email(dataset, config)


if __name__ == "__main__":
    main()
