from app.models.paleobiodb_record import PaleobiodbRecord


def test_from_dict(api_single_record):
    record = PaleobiodbRecord.from_api_dict(api_single_record)

    assert record.occurrence_id == "occ:1262350"
    assert record.taxon_id == "Triceratops sp."
    assert record.taxon_name == "Triceratops horridus"
    assert record.rank == 5

    assert record.latitude == 47.656944
    assert record.longitude == -107.33667

    assert record.early_interval == "Late Maastrichtian"
    assert record.late_interval is None

    assert record.early_age == 72.2
    assert record.late_age == 66.0

    assert record.phylogenetic_group == "Chordata"
    assert record.family_name == "Ceratopsidae"
    assert record.class_name == "Ornithischia"

    assert record.collection_id == "col:72143"
