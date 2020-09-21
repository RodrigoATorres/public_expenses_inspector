from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey

from .base import Base

class MscOrcamentaria(Base):
    __tablename__ = 'mscOrcamentaria'
    id = Column(Integer, primary_key=True)
    cod_ibge = Column(Integer, ForeignKey('entes.cod_ibge'))
    an_referencia = Column(Integer)
    me_referencia = Column(Integer)
    tipo_matriz = Column(String)
    classe_conta = Column(Integer)
    id_tv = Column(String)
    conta_contabil = Column(String)
    poder_orgao = Column(Integer)
    ano_fonte_recursos = Column(Integer)
    fonte_recursos = Column(String)
    funcao = Column(String)
    subfuncao = Column(String)
    exercicio = Column(Integer)
    mes_referencia = Column(Integer)
    educacao_saude =Column(Integer)
    data_referencia = Column(DateTime)
    entrada_msc = Column(Integer)
    natureza_despesa = Column(String)
    ano_inscricao = Column(Integer)
    natureza_receita = Column(String)
    valor = Column(Float)
    natureza_conta = Column(String)
    tipo_valor = Column(String)
   