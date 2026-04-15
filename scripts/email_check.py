from app.services.paleobiodb_email_sender import PaleobiodbEmailSender
from app.services.paleobiodb_dataset import PaleobiodbDataset
from app.config.config import Config
from app.config.config_paths import ENV_FILE, DATA_DIR


CSV_FILE_EXAMPLE = DATA_DIR.joinpath("example.csv")
MAIL_SUBJECT = "Paleobiodb – Maastrichtian Occurrences"
MAIL_TITLE = "Paleobiology Database – Maastrichtian Fossil Occurrences"


def run_email_report():

    cfg = Config(env_config_path=ENV_FILE)

    records = PaleobiodbDataset.from_csv(CSV_FILE_EXAMPLE)
    table = records.create_table_html()

    sender = PaleobiodbEmailSender(
        cfg.email_host,
        cfg.email_login,
        cfg.email_from,
        cfg.email_password,
        cfg.email_port,
        cfg.email_to
    )

    sender.send_html_report(subject=MAIL_SUBJECT,
                            title=MAIL_TITLE,
                            html_table=table)

if __name__ == "__main__":
    run_email_report()