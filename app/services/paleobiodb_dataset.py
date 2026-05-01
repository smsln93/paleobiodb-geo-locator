import logging
import csv
from dataclasses import fields, asdict
from typing import List
from pathlib import Path

from app.models.paleobiodb_record import PaleobiodbRecord
from app.utils.requests_utils import fetch_paleobiodb_content


logger = logging.getLogger(__name__)


class DatasetWriteError(Exception):
    """
    Raised when writing dataset to CSV fails.
    """
    pass


class DatasetReadError(Exception):
    """
    Raised when reading dataset from CSV fails.
    """
    pass


class PaleobiodbDataset(object):
    """
    Class used to collect records from PaleobioDB API and provides methods to work with the collected configs.

    Attributes:
        records (List[PaleobiodbRecord]): List of PaleobiodbRecord instances.
    """
    def __init__(self, paleobiodb_records: List[PaleobiodbRecord]):
        self.records = paleobiodb_records

    @classmethod
    def from_api(cls, base_url: str, geological_period: str, min_latitude: float, max_latitude: float,
                 min_longitude: float, max_longitude: float, query_parameters: str = "ident,phylo,class,coords") \
            -> PaleobiodbDataset:
        """
        Fetches configs from PaleoBiodb API and returns a dataset instance.

        :param base_url: Base URL for the Paleobiology Database API endpoint.
        :param geological_period: Geological time interval.
        :param min_latitude: Minimum latitude.
        :param max_latitude: Maximum latitude.
        :param min_longitude: Minimum longitude.
        :param max_longitude: Maximum longitude.
        :param query_parameters: Comma-separated query parameters to include.
        :return: PaleobiodbDataset instance with data fetched from PaleobioDB.
        :raises DataFetchError: If the PaleobioDB API request fails.
        """

        logger.debug("Loading PaleobioDB dataset from PaleobioDB API...")

        records: List[PaleobiodbRecord] = fetch_paleobiodb_content(base_url, geological_period, min_latitude,
                                                                   max_latitude, min_longitude, max_longitude,
                                                                   query_parameters)
        logger.debug("PaleobioDB dataset has been loaded successfully.")
        return cls(records)

    @classmethod
    def from_csv(cls, csv_filepath: Path) -> PaleobiodbDataset:
        """
        Creates an PaleobiodbDataset instance by using csv file containing records configs.

        :param csv_filepath: Path to csv file containing records configs.
        :return: PaleobiodbDataset instance.
        :raises DatasetReadError: If reading dataset from CSV fails.
        """
        if csv_filepath.suffix != ".csv":
            raise DatasetReadError(f"Invalid file type: {csv_filepath.suffix}. Dataset file is expected to be CSV.")

        logger.debug("Loading PaleobioDB dataset from CSV...")
        records: List[PaleobiodbRecord] = []
        try:
            with csv_filepath.open(mode="r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    records.append(PaleobiodbRecord.from_csv_dict(row))
        except (OSError, csv.Error) as read_err:
            raise DatasetReadError("Failed to write dataset to CSV file") from read_err

        logger.debug("PaleobioDB dataset has been loaded successfully.")
        return cls(records)

    def to_csv(self, csv_filepath: Path) -> None:
        """
        Writes the PaleobioDB configs into CSV file.
        It will create file if it doesn't exist.

        :param csv_filepath: Path to the output CSV file.
        :raises DatasetWriteError: If writing dataset to CSV fails.
        """
        logger.debug("Writing configs to CSV file...")
        try:
            with csv_filepath.open(mode='w', newline="") as csvfile:
                fieldnames = [field.name for field in fields(PaleobiodbRecord)]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for record in self.records:
                    writer.writerow(asdict(record))
        except (OSError, csv.Error) as write_err:
            raise DatasetWriteError("Failed to write dataset to CSV file") from write_err

        logger.debug("CSV write successful.")

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
        return [record for record in self.records if record.phylogenetic_group
                and record.phylogenetic_group.lower() == group_name.lower()]

    def filter_by_class(self, class_name: str) -> List[PaleobiodbRecord]:
        """
        Filters the records to include only those belonging to the specified class.

        :param class_name: Name of the class to filter by.
        :return: List of PaleobiodbRecord instances matching the specified class.
        """
        return [record for record in self.records if record.class_name
                and record.class_name.lower() == class_name.lower()]

    def limit(self, number: int) -> List[PaleobiodbRecord]:
        """
        Returns the first `number` records from the dataset.

        :param number: Maximum number of records to return.
        :return: List of PaleobiodbRecord instances limited to the specified count.
        """
        return self.records[:number]

    def __len__(self):
        """
        Calculates number of records.

        :return: Number of records.
        """
        return len(self.records)
