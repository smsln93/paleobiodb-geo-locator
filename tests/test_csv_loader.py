from app.services.paleobiodb_dataset import PaleobiodbDataset


def test_from_csv_loads_correct_number_of_records(csv_path):
    dataset = PaleobiodbDataset.from_csv(csv_path)
    assert len(dataset.records) == 4


def test_all_records_have_occurrence_id(csv_path):
    dataset = PaleobiodbDataset.from_csv(csv_path)
    for record in dataset.records:
        assert record.occurrence_id is not None


def test_cedrobaena_brinkman_record_matches_expected(csv_path):
    dataset = PaleobiodbDataset.from_csv(csv_path)

    cedrobaena_brinkman_record = next(record for record in dataset.records
        if record.occurrence_id == "occ:1007483"
    )

    assert cedrobaena_brinkman_record.occurrence_id == "occ:1007483"
    assert cedrobaena_brinkman_record.taxon_id == "txn:212698"
    assert cedrobaena_brinkman_record.taxon_name == "Cedrobaena brinkman"
    assert cedrobaena_brinkman_record.rank == 3
    assert cedrobaena_brinkman_record.class_name == "Reptilia"
    assert cedrobaena_brinkman_record.early_interval == "Late Maastrichtian"
    assert cedrobaena_brinkman_record.late_interval is None
    assert cedrobaena_brinkman_record.latitude == 48.008888
    assert cedrobaena_brinkman_record.longitude == -106.448608
    assert cedrobaena_brinkman_record.early_age == 72.2
    assert cedrobaena_brinkman_record.late_age == 66
    assert cedrobaena_brinkman_record.collection_id == "col:122906"
