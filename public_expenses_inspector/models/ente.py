from sqlalchemy import Column, Integer, String, Date, Boolean

from .base import Base

class Ente(Base):
    __tablename__ = 'entes'
    cod_ibge = Column(Integer, primary_key=True)
    ente = Column(String)
    capital = Column(Boolean)
    regiao = Column(String)
    uf = Column(String)
    esfera = Column(String)
    exercicio = Column(Integer)
    populacao = Column(Integer)
    cnpj = Column(String)
