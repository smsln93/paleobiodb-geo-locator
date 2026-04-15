import logging
import csv
from datetime import datetime
from dataclasses import fields, asdict
from typing import List, Optional
from pathlib import Path

from requests import RequestException

from app.models.paleobiodb_record import PaleobiodbRecord
from app.utils.requests_utils import fetch_paleobiodb_content
from app.config.config_paths import OUTPUT_DIR


logger = logging.getLogger(__name__)


class PaleobiodbDataset(object):
    """
    Class used to collect records from PaleobioDB API and provides methods to work with the collected configs.

    Attributes:
        records (List[PaleobiodbRecord]): List of PaleobiodbRecord instances.
    """
    def __init__(self, paleodb_records: List[PaleobiodbRecord]):
        self.records = paleodb_records

    @classmethod
    def from_api(cls, base_url: str, geological_period: str, min_latitude: float, max_latitude: float,
                 min_longitude: float, max_longitude: float, query_parameters: str = "ident,phylo,class,coords") \
            -> Optional[PaleobiodbDataset]:
        """
        Fetches configs from PaleoBiodb API and returns a dataset instance.

        :param base_url: Base URL for the Paleobiology Database API endpoint.
        :param geological_period: Geological time interval.
        :param min_latitude: Minimum latitude.
        :param max_latitude: Maximum latitude.
        :param min_longitude: Minimum longitude.
        :param max_longitude: Maximum longitude.
        :param query_parameters: Comma-separated query parameters to include.
        :return: PaleobiodbDataset instance, or None if there was an issue with teching configs from PaleobioDB.
        :raises: RequestException in case of an issue with API request.
        """

        logger.debug("Creating PaleobiodbDataset instance from fetching PaleobioDB configs...")
        try:
            records: List[PaleobiodbRecord] = fetch_paleobiodb_content(base_url, geological_period, min_latitude,
                                                                       max_latitude, min_longitude, max_longitude,
                                                                       query_parameters)
        except RequestException as req_exc:
            logger.error(f"Failed to fetch PaleobioDB configs: {req_exc}")
            return None
        else:
            logger.debug("PaleobiodbDataset instance has been created successfully.")
            return cls(records)

    @classmethod
    def from_csv(cls, csv_filepath: Path) -> PaleobiodbDataset:
        """
        Creates an PaleobiodbDataset instance by using csv file containing records configs.

        :param csv_filepath: Path to csv file containing records configs.
        :return: PaleobiodbDataset instance.
        :raises OSError: If there is a problem accessing the file or folder.
        :raises csv.Error: If there is an error with CSV formatting.
        """
        if csv_filepath.suffix != ".csv":
            raise ValueError("Invalid file type.")

        records: List[PaleobiodbRecord] = []
        logger.debug("Loading PaleobioDB dataset from CSV...")
        try:
            with csv_filepath.open("r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    records.append(PaleobiodbRecord.from_csv_dict(row))

        except OSError as os_err:
            logger.error(f"Failed to load configs from CSV file {csv_filepath}: {os_err}")
        except csv.Error as csv_err:
            logger.error(f"Failed to read CSV file {csv_filepath} due to formatting error: {csv_err}")

        logger.debug("PaleobioDB dataset has been loaded successfully.")
        return cls(records)

    def to_csv(self, custom_csv_filepath: Optional[Path] = None) -> bool:
        """
        Writes the PaleobioDB configs into CSV file.
        It will create file if it doesn't exist.

        :param custom_csv_filepath: Optional path to CSV file defined by the User.
        :return: True if file has been written successfully, False otherwise.
        :raises OSError: If there is a problem accessing the file or folder.
        :raises csv.Error: If there is an error with CSV formatting.
        """
        logger.debug("Writing configs to CSV file...")
        try:
            if custom_csv_filepath is None:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                csv_filename = f"PaleobiodbDataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_filepath = OUTPUT_DIR.joinpath(csv_filename)
            else:
                csv_filepath = custom_csv_filepath

            if csv_filepath.suffix != ".csv":
                raise ValueError("Invalid file type.")

            with csv_filepath.open('w', newline="") as csvfile:
                fieldnames = [field.name for field in fields(PaleobiodbRecord)]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for record in self.records:
                    writer.writerow(asdict(record))
        except OSError as os_err:
            logger.error(f"CSV write failed (OS error): {os_err}.")
            return False
        except csv.Error as csv_err:
            logger.error(f"CSV write failed (format error): {csv_err}.")
            return False
        logger.debug("CSV write successful.")
        return True

    def filter_species(self) -> List[PaleobiodbRecord]:
        """
        Filters the records to include only those ranked as species.

        :return: List of PaleobiodbRecord instances ranked as "species".
        """
        return [record for record in self.records if record.is_species()]

    def filter_by_phylogenetic_group(self, group_name: str) -> List[PaleobiodbRecord]:
        """
        Filters the records to include only those belonging to the specified phylogenetic group.

        :param group_name: Name of the phylogenetic group to filter by.
        :return: List of PaleobiodbRecord instances matching the specified group.
        """
        return [record for record in self.records if record.phylogenetic_group.lower() == group_name.lower()]

    def filter_by_class(self, class_name: str) -> List[PaleobiodbRecord]:
        """
        Filters the records to include only those belonging to the specified class.

        :param class_name: Name of the class to filter by.
        :return: List of PaleobiodbRecord instances matching the specified class.
        """
        return [record for record in self.records if record.class_name.lower() == class_name.lower()]

    def limit(self, number: int) -> List[PaleobiodbRecord]:
        """
        Returns the first `number` records from the dataset.

        :param number: Maximum number of records to return.
        :return: List of PaleobiodbRecord instances limited to the specified count.
        """
        return self.records[:number]

    def create_table_html(self) -> str:
        """
        Outputs HTML styled table out of the PalebioDB records.

        :return: HTML table containing PalebioDB configs.
        """
        table_style = """
        <style>
            table {
                font-family: Arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
                max-width: 800px;
                border: 1px solid #dddddd;
            }

            th {
                border: 1px solid #dddddd;
                text-align: center;
                padding: 8px;
                background-color: #f2f2f2;
            }

            td {
                border: 1px solid #dddddd;
                text-align: center;
                padding: 8px;
            }

            .left-align {
                text-align: left;
            }
        </style>
        """

        table_body = ""
        for record in self.records:
            table_body += f"""
                    <tr>
                        <td>{record.taxon_name or "N/A"}</td>
                        <td>{record.family_name or "N/A"}</td>
                        <td>{record.location}</td>
                        <td>{record.interval_range}</td>
                        <td>{record.age_range}</td>
                        <td>{record.collection_id or "N/A"}</td>
                    </tr>"""

        table_html = f"""
                    <table>
                        {table_style}
                        <thead>
                            <tr>
                                <th> Taxon name </th>
                                <th> Taxon family name </th>
                                <th> Location geographic coordinates </th>
                                <th> Interval range </th>
                                <th> Age range (in Ma)</th>
                                <th> Collection ID </th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_body}
                        </tbody>
                    </table>
                """
        return table_html

    def __len__(self):
        """
        Calculates number of records.

        :return: Number of records.
        """
        return len(self.records)
