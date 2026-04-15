from app.config.config import Config


def test_load_config_from_file(example_app_config, example_env_config):

    cfg = Config(app_config_path=example_app_config, env_config_path=example_env_config)

    assert cfg.base_url == "https://paleobiodb.org/data1.2/occs/list.json"
    assert cfg.send_email == False
    assert cfg.min_latitude == 44.5
    assert cfg.max_latitude == 49.0
    assert cfg.min_longitude == -106.0
    assert cfg.max_longitude == -100.0
    assert cfg.interval == "Maastrichtian"
    assert cfg.query_parameters == "ident,phylo,class,coords"

    assert cfg.email_host == "example.host.123"
    assert cfg.email_port == 123
    assert cfg.email_from == "example.address@domain.com"
    assert cfg.email_to == ["test1@mail.com", "test2@mail.com"]
    assert cfg.email_login == "example.login"
    assert cfg.email_password == "examplepass123"