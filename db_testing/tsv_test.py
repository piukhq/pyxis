import uuid

import psycopg2
import csv
import time
from faker import Faker



fake = Faker()

TOTAL = 1000000

all_data = []


def generate_data():
    for i in range(TOTAL):
        all_data.append([fake.name() + str(uuid.uuid4()), fake.pyint()])

    with open("test_data.tsv", "w+") as f:
        tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
        tsv_writer.writerows(all_data)


def load_data():
    with psycopg2.connect("postgresql://postgres:Tunners07DB@localhost:5432/dolos") as connection:
        with connection.cursor() as cursor:
            with open("test_data.tsv") as f:
                cursor.copy_from(f, "test", sep="\t", null="NULL")


def truncate_table():
    with psycopg2.connect("postgresql://postgres:Tunners07DB@localhost:5432/dolos") as connection:
        with connection.cursor() as cursor:
            truncate_statement = f'TRUNCATE "test" CASCADE'
            cursor.execute(truncate_statement)

timez = time.time()

truncate_table()
generate_data()
load_data()


print(f"COMPLETED IN {time.time() - timez} seconds.")
