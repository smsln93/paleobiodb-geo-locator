from dataclasses import dataclass, fields
from typing import Dict, Tuple, Optional
import re


FIELD_MAPPING_API = {
    "oid": "occurrence_id",
    "idn": "taxon_id",
    "tna": "taxon_name",
    "rnk": "rank",
    "phl": "phylogenetic_group",
    "fml": "family_name",
    "cll": "class_name",
    "lat": "latitude",
    "lng": "longitude",
    "oei": "early_interval",
    "oli": "late_interval",
    "eag": "early_age",
    "lag": "late_age",
    "cid": "collection_id",
}


@dataclass
class PaleobiodbRecord:
    """
    Describes single record of configs fetched from PaleobioDB.
    """
    occurrence_id: str
    taxon_id: Optional[str]
    taxon_name: Optional[str]
    rank: Optional[int]
    phylogenetic_group: Optional[str]
    family_name: Optional[str]
    class_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    early_interval: Optional[str]
    late_interval: Optional[str]
    early_age: Optional[float]
    late_age: Optional[float]
    collection_id: Optional[str]

    @property
    def location(self) -> Tuple[float, float]:
        """
        Returns geographic coordinates of the specimen.

        :return: Tuple of (latitude, longitude).
        """

        if self.latitude is None or self.longitude is None:
            raise ValueError("Either latitude or longitude is required.")

        return self.latitude, self.longitude

    @property
    def interval_range(self) -> str:
        """
        Returns interval range of the specimen.

        :return: String representing range (early interval - late interval)
        or N/A if no early or late interval configs is specified in PaleobioDB.
        """
        if self.early_interval and self.late_interval:
            return f"{self.early_interval} - {self.late_interval}"
        elif self.early_interval:
            return f"{self.early_interval}"
        elif self.late_interval:
            return f"{self.late_interval}"
        else:
            return "N/A"

    @property
    def age_range(self) -> str:
        """
        Returns age range in Ma of the specimen.

        :return: String representing range (early age - late age) or N/A if proper configs is not specified in PaleobioDB.
        """
        if self.early_age is not None and self.late_age is not None:
            return f"{self.early_age:.2f}-{self.late_age:.2f}"
        return "N/A"


    @classmethod
    def from_api_dict(cls, data_dict: Dict[str, Optional[str]]) -> "PaleobiodbRecord":
        """
        Creates a PaleobiodbRecord instance from a dictionary.
        Uses only key matching the dataclass fields, the rest is ignored.

        :param data_dict: Dictionary containing configs.
        :return: PaleobiodbRecord instance.
        """

        mapped = {
            model_key: data_dict.get(api_key)
            for api_key, model_key in FIELD_MAPPING_API.items()
        }

        oid = cls._normalize_value(mapped["occurrence_id"])

        if oid is None:
            raise ValueError("Occurence ID is required.")

        return cls(
            occurrence_id=oid,
            taxon_id=cls._normalize_value(mapped["taxon_id"]),
            taxon_name=cls._normalize_value(mapped["taxon_name"]),
            rank=cls._to_int(mapped["rank"]),
            phylogenetic_group=cls._normalize_value(mapped["phylogenetic_group"]),
            family_name=cls._normalize_value(mapped["family_name"]),
            class_name=cls._normalize_value(mapped["class_name"]),
            latitude=cls._to_float(mapped["latitude"]),
            longitude=cls._to_float(mapped["longitude"]),
            early_interval=cls._normalize_value(mapped["early_interval"]),
            late_interval=cls._normalize_value(mapped["late_interval"]),
            early_age=cls._to_float(mapped["early_age"]),
            late_age=cls._to_float(mapped["late_age"]),
            collection_id=cls._normalize_value(mapped["collection_id"]),
        )

    @classmethod
    def from_csv_dict(cls, data_dict: Dict[str, Optional[str]]) -> "PaleobiodbRecord":
        """
        Creates a PaleobiodbRecord instance from a dictionary.
        Uses only key matching the dataclass fields, the rest is ignored.

        :param data_dict: Dictionary containing configs.
        :return: PaleobiodbRecord instance.
        """

        oid = cls._normalize_value(data_dict.get("occurrence_id"))
        if oid is None:
            raise ValueError("Occurence ID is required.")

        return cls(
            occurrence_id=oid,
            taxon_id=cls._normalize_value(data_dict.get("taxon_id")),
            taxon_name=cls._normalize_value(data_dict.get("taxon_name")),
            rank=cls._to_int(data_dict.get("rank")),
            phylogenetic_group=cls._normalize_value(data_dict.get("phylogenetic_group")),
            family_name=cls._normalize_value(data_dict.get("family_name")),
            class_name=cls._normalize_value(data_dict.get("class_name")),
            latitude=cls._to_float(data_dict.get("latitude")),
            longitude=cls._to_float(data_dict.get("longitude")),
            early_interval=cls._normalize_value(data_dict.get("early_interval")),
            late_interval=cls._normalize_value(data_dict.get("late_interval")),
            early_age=cls._to_float(data_dict.get("early_age")),
            late_age=cls._to_float(data_dict.get("late_age")),
            collection_id=cls._normalize_value(data_dict.get("collection_id"))
        )

    def to_dict(self) -> Dict[str, str]:
        """
        Saves PaleobioDB record into dictionary.

        :return: Dictionary containing PaleobioDB record configs.
        """
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def is_species(self) -> bool:
        """
        Checks if record describes a species.

        :return: True if record describes a spiecies, false otherwise.
        """
        return self.rank == 5

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the PaleobioDB record instance.

        :return: String describing the record (taxon, phylo, class, location, interval).
        """
        return f"Record from PaleobioDB: {self.taxon_name}," \
               f"({self.phylogenetic_group}, {self.class_name}) " \
               f"at location ({self.latitude:.2f}, {self.longitude:.2f}) " \
               f"dated between: {self.early_interval} and {self.late_interval}"

    def __repr__(self) -> str:
        """
        Returns a developre-oriented representation of the PaleobioDB record instance.

        :return: String suitable for debugging, showing class name and key fields.
        """
        return f"PaleobiodbRecord(" \
               f"occurence_id={self.occurrence_id}," \
               f"taxon_id={self.taxon_id}," \
               f"taxon_name={self.taxon_name}," \
               f"rank={self.rank}," \
               f"phylogenetic_group={self.phylogenetic_group}," \
               f"family_name={self.family_name}," \
               f"class_name={self.class_name}," \
               f"latitude={self.latitude:.2f}," \
               f"longitude={self.longitude:.2f}," \
               f"early_interval={self.early_interval}," \
               f"late_interval={self.late_interval}," \
               f"early_age={self.early_age:.2f}," \
               f"late_age={self.late_age:.2f}," \
               f"collection_id={self.collection_id})"

    @staticmethod
    def _normalize_value(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value_str = str(value).strip()

        if not value_str:
            return None

        pattern = r"no_.+specified|not\sentered|not\sprovided|not\sspecified"

        if re.search(pattern, value_str, re.IGNORECASE):
            return None
        return value_str

    @classmethod
    def _to_int(cls, value: Optional[str]) -> Optional[int]:
        value = cls._normalize_value(value)

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _to_float(cls, value: Optional[str]) -> Optional[float]:
        value = cls._normalize_value(value)

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
