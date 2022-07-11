#!/usr/bin/env python
from retry_tasks_lib.db.models import TaskType, load_models_to_metadata
from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from settings import DB_CONNECTION_URI


def get_session(DB: str | bool | None) -> "Session":
    db_connection_string: str = DB_CONNECTION_URI.replace("/postgres?", f"/{DB}?")

    sync_engine = create_engine(db_connection_string, echo=False, pool_pre_ping=True, future=True, poolclass=NullPool)
    SyncSessionMaker = sessionmaker(bind=sync_engine, future=True, expire_on_commit=False)
    db_session = SyncSessionMaker()

    return db_session


Base = declarative_base()
load_models_to_metadata(Base.metadata)


def get_task_type(db_session: "Session", task_name: str) -> TaskType:
    task_type = (
        db_session.execute(
            select(TaskType).filter(
                TaskType.name == task_name,
            )
        )
        .scalars()
        .first()
    )
    return task_type
