from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from faker import Faker

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


class DB:
    """This is a singleton class to manage sessions.

    To use the singleton import the DB class then:

    with DB().open as session:
    """

    def __init__(self, connection_string):

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


class PolarisDB(DB, metaclass=Singleton):
    def __init__(self):
        self.connection_string = "postgresql://postgres:Tunners07DB@localhost:5432/polaris"
        super().__init__(self.connection_string)


