import psycopg2
from settings import DB_CONNECTION_URI, POLARIS_DB
from data_population.database_tables import PolarisTables
import logging

class DataTaskHandler:

    def __init__(self):
        self.db_name = POLARIS_DB
        self.tables = PolarisTables

    def repopulate_tables():
        connection_string = DB_CONNECTION_URI.replace("/postgres", f"/{POLARIS_DB}")

        with psycopg2.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                logger.debug(f"Truncating tables defined in '{tables}'")
                for table in tables:
                    truncate_table(cursor, table)