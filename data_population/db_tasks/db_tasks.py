import os
import logging

import psycopg2

import settings
from settings import DB_CONNECTION_URI, POLARIS_DB, VELA_DB, CARINA_DB, TSV_BASE_DIR
from data_population.database_tables import PolarisTables
from os import listdir
import logging

logger = logging.getLogger('DataTaskHandler')


class DataTaskHandler:

    def repopulate_all_databases(self):

        polaris_tsvs = []
        vela_tsvs = []
        carina_tsvs = []

        #  Sort tables per db
        for tsv in self.all_tsv_info:
            if tsv['db'] == POLARIS_DB:
                polaris_tsvs.append(tsv)
            elif tsv['db'] == VELA_DB:
                vela_tsvs.append(tsv)
            elif tsv['db'] == CARINA_DB:
                carina_tsvs.append(tsv)

        #  Upload tables per db
        # self.truncate_and_upload(tsv_list=vela_tsvs, db_name=VELA_DB)
        # self.truncate_and_upload(tsv_list=carina_tsvs, db_name=CARINA_DB)
        print(polaris_tsvs)
        self.truncate_and_repopulate_all_tables(tsv_info_list=polaris_tsvs, db_name=POLARIS_DB)

    @staticmethod
    def truncate_and_repopulate_all_tables(tsv_info_list: list, db_name: str):
        logger.info(f'Repopulating tables in {db_name.upper()}...')

        connection = DB_CONNECTION_URI[:-9] + '/' + db_name

        with psycopg2.connect(connection) as connection:
            with connection.cursor() as cursor:
                for tsv_info in tsv_info_list:

                    table_name = tsv_info["table"]
                    file_name = tsv_info["filename"]

                    # TRUNCATE
                    logger.info(f'Truncating {db_name} table {table_name}')
                    truncate_statement = f'TRUNCATE "{table_name}" CASCADE'
                    cursor.execute(truncate_statement)
                    logger.info(f'Truncated {db_name} table {table_name}')

                    # UPLOAD/COPY
                    with open(os.path.join(TSV_BASE_DIR, file_name)) as f:
                        cursor.copy_from(f, table_name, sep="\t", null="NULL")
                    logger.info(f'Uploaded data to table {table_name} from {file_name}')

    @property
    def all_tsv_info(self):
        tsv_data = []
        for tsv in os.listdir(settings.PROJECT_ROOT + "/" + TSV_BASE_DIR):
            tsv_parts = tsv.replace('.tsv', '').split("-")
            tsv_data.append({
                "filename": tsv,
                "db": tsv_parts[1],
                "table": tsv_parts[3],
                "order": int(tsv_parts[2])
            })

        tsv_data.sort(key=lambda i: i['order'])

        return tsv_data  # tables populated in order they were created
