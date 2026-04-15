import pytest
from pathlib import Path
from typing import Dict, Any

from app.models.paleobiodb_record import PaleobiodbRecord
from app.config.config_paths import DATA_DIR


TEST_DATA_DIR = Path(__file__).parent.joinpath("configs")

@pytest.fixture
def csv_path():
    return DATA_DIR.joinpath("example.csv")


@pytest.fixture
def example_app_config():
    return TEST_DATA_DIR.joinpath("example_config.toml")


@pytest.fixture
def example_env_config():
    return TEST_DATA_DIR.joinpath("env.example")


@pytest.fixture
def sample_record():
    return PaleobiodbRecord(
        occurrence_id="occ:1",
        taxon_id= "Triceratops sp.",
        taxon_name="Triceratops horridus",
        rank=5,
        phylogenetic_group="Chordata",
        family_name="Ceratopsidae",
        class_name="Ornithischia",
        latitude=50.0,
        longitude=20.0,
        early_interval="Late Maastrichtian",
        late_interval=None,
        early_age=72.2,
        late_age=66.0,
        collection_id="col:1"
    )


@pytest.fixture
def api_single_record() -> Dict[str, Any]:
    return {
        "oid": "occ:1262350",
        "cid": "col:72143",
        "idn": "Triceratops sp.",
        "tna": "Triceratops horridus",
        "rnk": 5,
        "tid": "txn:38862",
        "oei": "Late Maastrichtian",
        "eag": 72.2,
        "lag": 66,
        "rid": "ref:54744",
        "idg": "Triceratops",
        "ids": "sp.",
        "phl": "Chordata",
        "cll": "Ornithischia",
        "odl": "NO_ORDER_SPECIFIED",
        "fml": "Ceratopsidae",
        "gnl": "Triceratops",
        "lng": "-107.336670",
        "lat": "47.656944"
    }
