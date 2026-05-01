import csv
from app.services.paleobiodb_dataset import PaleobiodbDataset


def test_to_csv_writes_correct_data(tmp_path, sample_record):
    output_file = tmp_path.joinpath("output.csv")

    dataset = PaleobiodbDataset(paleobiodb_records=[sample_record])

    dataset.to_csv(output_file)

    assert output_file.exists()

    with open(output_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1

    row = rows[0]
    assert row["occurrence_id"] == "occ:1"
    assert row["taxon_id"] == "Triceratops sp."
    assert row["taxon_name"] == "Triceratops horridus"
    assert row["rank"] == "5"
    assert row["phylogenetic_group"] == "Chordata"
    assert row["family_name"] == "Ceratopsidae"
    assert row["class_name"] == "Ornithischia"
    assert row["latitude"] == "50.0"
    assert row["longitude"] == "20.0"
    assert row["early_interval"] == "Late Maastrichtian"
    assert row["late_interval"] == ""
    assert row["early_age"] == "72.2"
    assert row["late_age"] == "66.0"
    assert row["collection_id"] == "col:1"
