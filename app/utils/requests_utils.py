import requests
import logging
from typing import List
from app.models.paleobiodb_record import PaleobiodbRecord


logger = logging.getLogger(__name__)


class DataFetchError(Exception):
    """
    Raised when the PaleobioDB API request fails or returns an invalid response.
    """
    pass


def fetch_paleobiodb_content(base_url: str,
                             geological_period: str,
                             min_latitude: float,
                             max_latitude: float,
                             min_longitude: float,
                             max_longitude: float,
                             query_parameters: str) -> List[PaleobiodbRecord]:
    """
    Fetches records from the Paleobiology Database for a given geolocation and interval.

    :param base_url: Base URL for the Paleobiology Database API endpoint.
    :param geological_period: Geological time interval.
    :param min_latitude: Minimum latitude.
    :param max_latitude: Maximum latitude.
    :param min_longitude: Minimum longitude.
    :param max_longitude: Maximum longitude.
    :param query_parameters: Comma-separated query parameters to include.
    :return: List of PaleoRecord instances.
    :raises DataFetchError: If the PaleobioDB API request fails or returns an invalid response.
    """
    logger.debug("Fetching records from the Paleobiology Database")

    params = {
        "interval": geological_period,
        "latmin": min_latitude,
        "latmax": max_latitude,
        "lngmin": min_longitude,
        "lngmax": max_longitude,
        "query_parameters": query_parameters
    }

    try:
        paleobiodb_response = requests.get(url=base_url, params=params, timeout=10)
        paleobiodb_response.raise_for_status()
        data = paleobiodb_response.json()
        return [PaleobiodbRecord.from_api_dict(record) for record in data.get("records", [])]
    except requests.RequestException as req_exc:
        raise DataFetchError(f"Failed to fetch paleobiodb data.") from req_exc
