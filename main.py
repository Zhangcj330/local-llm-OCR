from src.page_processor import PageProcessor

page_processor = PageProcessor()
results = page_processor.process_file("SAMPLE-TAL Medical Examiner's Confidential Report.pdf", verbose=True, model_type="gemini")


# export to db
host = "localhost"
database = "medical_reports_db"
username = "root"
password = "MyRootPass123"
port = 3306
table_name = "medical_reports"
update_on_duplicate = True
create_table_if_not_exists = True


results.to_mysql_db_grouped(
            host=host,
            database=database,
            username=username,
            password=password,
            port=port
        )
