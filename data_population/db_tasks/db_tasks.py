import os

import psycopg2

import settings
from settings import DB_CONNECTION_URI, POLARIS_DB, VELA_DB, CARINA_DB, TSV_BASE_DIR
import logging

logger = logging.getLogger("DataTaskHandler")


class DataTaskHandler:
    """Handles whole Data Upload journey for all databases."""

    def repopulate_all_databases(self):
        """Sorts all_tsv_info per database and executes per-database truncation and copy tasks."""

        polaris_tsvs = []
        vela_tsvs = []
        carina_tsvs = []

        #  Sort tables per db
        for tsv in self.all_tsv_info:
            if tsv["db"] == POLARIS_DB:
                polaris_tsvs.append(tsv)
            elif tsv["db"] == VELA_DB:
                vela_tsvs.append(tsv)
            elif tsv["db"] == CARINA_DB:
                carina_tsvs.append(tsv)

        #  Upload tables per db
        self.truncate_and_repopulate_all_tables(tsv_info_list=vela_tsvs, db_name=VELA_DB)
        self.truncate_and_repopulate_all_tables(tsv_info_list=carina_tsvs, db_name=CARINA_DB)
        self.truncate_and_repopulate_all_tables(tsv_info_list=polaris_tsvs, db_name=POLARIS_DB)

    @staticmethod
    def truncate_and_repopulate_all_tables(tsv_info_list: list, db_name: str):
        """
        (Per table/tsv): Truncates table and then copies in new data from tsv.

        :param tsv_info_list: list of dictionaries containing information about which table and database each tsv should
         be loaded to, and in what order.
        :param db_name: name of database to act on.
        """

        logger.info(f"{db_name.upper()}: Beginning database re-population ...")

        connection = DB_CONNECTION_URI[:-9] + "/" + db_name

        with psycopg2.connect(connection) as connection:
            with connection.cursor() as cursor:
                for tsv_info in tsv_info_list:

                    table_name = tsv_info["table"]
                    file_name = tsv_info["filename"]

                    # TRUNCATE
                    logger.info(f"{db_name.upper()}: {table_name}: Attempting to truncate table")
                    truncate_statement = f'TRUNCATE "{table_name}" CASCADE'
                    cursor.execute(truncate_statement)
                    logger.info(f"{db_name.upper()}: {table_name}: Successfully truncated table")

                    # UPLOAD/COPY
                    logger.info(f"{db_name.upper()}: {table_name}: Attempting to copy data into table")
                    with open(os.path.join(TSV_BASE_DIR, file_name)) as f:
                        cursor.copy_from(f, table_name, sep="\t", null="NULL")
                    logger.info(f"{db_name.upper()}: {table_name}: Successfully uploaded data")

        logger.info(f"{db_name.upper()}: All tables successfully repopulated")

    @property
    def all_tsv_info(self) -> [dict]:
        """
        :return: list of dictionaries containing information about which table and database each tsv should
         be loaded to, and in what order.
        """
        tsv_data = []

        for tsv in [f for f in os.listdir(settings.PROJECT_ROOT + "/" + TSV_BASE_DIR) if f[-4:] == ".tsv"]:
            tsv_parts = tsv.replace(".tsv", "").split("-")
            tsv_data.append({"filename": tsv, "db": tsv_parts[1], "table": tsv_parts[3], "order": int(tsv_parts[2])})

        tsv_data.sort(key=lambda i: i["order"])  # tables sorted and populated in order they were created

        return tsv_data
