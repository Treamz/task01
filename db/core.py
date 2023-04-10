from sqlmodel import (
    SQLModel, 
    create_engine, 
    Session, 
)
from sqlalchemy.engine import Engine

from settings import settings



engine = create_engine(url=f'sqlite:///{settings.db_path}')

def create_delete_db(create: bool = True, engine: Engine = engine) -> None:
    from models.core import Account, Session
    if create:
        SQLModel.metadata.create_all(engine)
    else:
        SQLModel.metadata.drop_all(engine)

def get_session(engine: Engine = engine) -> Session:
    with Session(bind=engine) as session:
        yield session
