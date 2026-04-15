import pytest
import requests
from unittest.mock import patch, Mock

from app.utils.requests_utils import fetch_paleobiodb_content


@patch("app.utils.requests_utils.requests.get")
def test_fetch_paleobiodb_content_builds_correct_params(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"records": []}
    mock_get.return_value = mock_response

    from app.utils.requests_utils import fetch_paleobiodb_content

    fetch_paleobiodb_content(
        base_url="https://paleobiodb.org/api/v1/occs/list",
        geological_period="Furongian",
        min_latitude=10.0,
        max_latitude=20.0,
        min_longitude=30.0,
        max_longitude=40.0,
        query_parameters="coords"
    )

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    assert kwargs["url"] == "https://paleobiodb.org/api/v1/occs/list"
    assert kwargs["timeout"] == 10

    params = kwargs["params"]

    assert params["latmin"] == 10.0
    assert params["latmax"] == 20.0
    assert params["lngmin"] == 30.0
    assert params["lngmax"] == 40.0
    assert params["interval"] == "Furongian"
    assert params["show"] == "coords"


@patch("app.utils.requests_utils.requests.get")
def test_fetch_paleobiodb_returns_edmontosaurus_records(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    mock_response.json.return_value = {
        "records": [
            {
                "oid":"occ:1123612",
                "cid":"col:72143",
                "idn":"Edmontosaurus sp.",
                "tna":"Edmontosaurus",
                "rnk":5,
                "tid":"txn:38761",
                "oei":"Late Maastrichtian",
                "eag":72.2,
                "lag":66,
                "rid":"ref:46207",
                "idg":"Edmontosaurus",
                "ids":"sp.",
                "phl":"Chordata",
                "cll":"Ornithischia",
                "odl":"NO_ORDER_SPECIFIED",
                "fml":"Hadrosauridae",
                "gnl":"Edmontosaurus",
                "lng":"-107.336670",
                "lat":"47.656944"}
        ]}

    mock_get.return_value = mock_response

    records = fetch_paleobiodb_content(
        base_url="https://paleobiodb.org/api/v1/occs/list",
        geological_period="Maastrichtian",
        min_latitude=45.0,
        max_latitude=49.0,
        min_longitude=-110.0,
        max_longitude=-100.0,
        query_parameters="ident,phylo,class,coords"
    )

    assert len(records) == 1

    edmontosaurus_record = records[0]

    assert edmontosaurus_record.occurrence_id == "occ:1123612"
    assert edmontosaurus_record.taxon_id == "Edmontosaurus sp."
    assert edmontosaurus_record.taxon_name == "Edmontosaurus"
    assert edmontosaurus_record.rank == 5
    assert edmontosaurus_record.phylogenetic_group == "Chordata"
    assert edmontosaurus_record.family_name == "Hadrosauridae"
    assert edmontosaurus_record.class_name == "Ornithischia"
    assert edmontosaurus_record.latitude == 47.656944
    assert edmontosaurus_record.longitude == -107.336670
    assert edmontosaurus_record.early_interval == "Late Maastrichtian"
    assert edmontosaurus_record.late_interval is None
    assert edmontosaurus_record.early_age == 72.2
    assert edmontosaurus_record.late_age == 66
    assert edmontosaurus_record.collection_id == "col:72143"


@patch("app.utils.requests_utils.requests.get")
def test_fetch_empty_response(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    mock_response.json.return_value = {
        "records": []
    }

    mock_get.return_value = mock_response

    result = fetch_paleobiodb_content(
        base_url="https://paleobiodb.org/api/v1/occs/list",
        geological_period="Maastrichtian",
        min_latitude=45.0,
        max_latitude=49.0,
        min_longitude=-110.0,
        max_longitude=-100.0,
        query_parameters="ident,phylo,class,coords"
    )

    assert result == []


@patch("app.utils.requests_utils.requests.get")
def test_fetch_api_exception(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        fetch_paleobiodb_content(
            base_url="https://paleobiodb.org/api/v1/occs/list",
            geological_period="Maastrichtian",
            min_latitude=45.0,
            max_latitude=49.0,
            min_longitude=-110.0,
            max_longitude=-100.0,
            query_parameters="ident,phylo,class,coords"
        )
