from models.ente import Ente
from models.mscOrcamentaria import MscOrcamentaria
from models.budgetSummary import BudgetSummary
from sqlalchemy.orm import sessionmaker
import pandas as pd

def calcBudgetSummary(db_engine, cod_ibge, year, month):
    Session = sessionmaker()
    Session.configure(bind = db_engine)
    session = Session()
    query = session.query(Ente)
        .filter( MscOrcamentaria.cod_ibge == cod_ibge )
        .filter( MscOrcamentaria.an_referencia == year )
        .filter( MscOrcamentaria.me_referencia == month )
    
    query(Table.column, func.count(Table.column), func.sum() ).group_by(Table.column).all()
