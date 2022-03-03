import uuid

from sqlalchemy import MetaData, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from faker import Faker

import time

fake = Faker()

class Singleton(type):
    """
    This is a basic singleton metaclass which works as expected if not threaded in Python or by Gunicorn/WSGI
    If used threaded the first thread would set up the instance and other threads would get the same data.
    This would persist across threads and requests.
    NB.  We may need to add a lock for additional safety
    """

    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class DB(metaclass=Singleton):
    """This is a singleton class to manage sessions.

    To use the singleton import the DB class then:

    with DB().open as session:
    """

    def __init__(self):
        """Note as a singleton will only run on first instantiation"""

        connection_string = "postgresql://postgres:Tunners07DB@localhost:5432/dolos"

        self.engine = create_engine(connection_string)
        self.metadata = MetaData(bind=self.engine)

        self.Base = declarative_base()

        self.Session = scoped_session(sessionmaker(bind=self.engine, future=True))
        self.session = None

    def __enter__(self):
        """Return session to the variable referenced in the "with as" statement"""
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """Returns self to allow with clause to work and to allow chaining eg db().open_read().session"""
        self.session = self.Session()
        return self

    def close(self):
        self.session.close()


db = DB()


class Test(DB().Base):
    __table__ = Table("test", DB().metadata, autoload=True)


TOTAL = 100000


def truncate_table():
    with DB().open() as session:

        session.execute(Test.__table__.delete())
        session.commit()

def create_items():
    all_data = []

    for i in range(TOTAL):
        all_data.append(Test(
            test_column=fake.name() + str(uuid.uuid4()),
            type=fake.pyint()
        ))

    return all_data


def create_items_as_list():
    all_data = []

    for i in range(TOTAL):
        item = Test(
            test_column=fake.name() + str(uuid.uuid4()),
            type=fake.pyint()
        )
        all_data.append(item)
        print(list(item.__dict__.values())[1:])

    return all_data

def add_items (all_data):
    with DB().open() as session:
        session.bulk_save_objects(all_data)
        session.commit()


def add_items_engine(all_data):
    engine = DB().engine
    engine.execute(Test.__table__.insert(all_data))


timez = time.time()

truncate_table()
data = create_items()
add_items_engine(data)

print(f"COMPLETED IN {time.time() - timez} seconds")



