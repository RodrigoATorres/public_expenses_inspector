from models.ente import Ente
from sqlalchemy.orm import sessionmaker


def getEntes(db_engine, **kargs):
    Session = sessionmaker()
    Session.configure(bind = db_engine)
    session = Session()
    query = session.query(Ente)
    for key in kargs.keys():
        query = query.filter( getattr(Ente, key) == kargs[key] )
    return query