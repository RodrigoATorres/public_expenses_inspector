from dotenv import load_dotenv
load_dotenv()

from data_sources import sincofi

sincofiDriver = sincofi.SiconfiDriver()
sincofiDriver.getMunicipalData('MG','Belo Horizonte','Executivo','Prefeitura','2020')