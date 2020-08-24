from dotenv import load_dotenv
load_dotenv()
import os

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from models.base import Base
from models.ente import Ente

from data_sources import sincofi

engine = create_engine('{}://{}:{}@{}/{}'.format(
    os.getenv('DB_ENGINE'),
    os.getenv('DB_USERNAME'),
    os.getenv('DB_PASSWORD'),
    os.getenv('DB_URL'),
    os.getenv('DB_NAME')
))
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)

sincofiApi = sincofi.SiconfiAPIFetcher(engine)
sincofiApi.getEntes()

# sincofiDriver = sincofi.SiconfiDriver()
# sincofiDriver.getMunicipalData('MG','Belo Horizonte','Executivo','Prefeitura','2020')