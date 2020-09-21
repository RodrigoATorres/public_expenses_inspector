import os
import shutil
from pathlib import Path
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from helpers.captcha import imageCaptchaSolver

from sqlalchemy.orm import sessionmaker

from models.ente import Ente
from models.mscOrcamentaria import MscOrcamentaria

import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests

class SiconfiDriver:

    def __init__(self, delay_period = 5):
        self.delay_period = delay_period
        self.startDriver()


    def startDriver(self):

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", os.path.join(os.getcwd(), 'data/siconfi/tmp'))
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
        self.driver = webdriver.Firefox(firefox_profile=profile)
        self.driver.get("https://siconfi.tesouro.gov.br/siconfi/pages/public/declaracao/declaracao_list.jsf")
        self.actionChains = ActionChains(self.driver)
        assert "Siconfi" in self.driver.title

    def closeDriver(self):
        self.driver.close()

    def getMunicipalData(self, estado, ente, poder, orgao, exercicio, max_tries = 3, n_tries = 1):
        self.getEsferaOptions()
        self.selectEsfera('Municipal')
        time.sleep(5)
        opts = self.getEstadoOptions()
        self.selectEstado(estado)
        time.sleep(5)   
        self.selectEnte(ente)
        time.sleep(5)
        opts = self.getPoderOptions()
        self.selectPoder(poder)
        self.selectOrgao(orgao)
        time.sleep(5)
        opts = self.getExercicioOptions()
        self.selectExercicio(exercicio)
        self.saveCaptchaImage()
        captcha_text = imageCaptchaSolver('captcha.png')
        self.inputCatcha(captcha_text)
        time.sleep(5)
        self.downloadAllXBRL()

        dir_path = "{}/data/siconfi/{}/{}/{}/{}/{}".format(os.getcwd(),estado, ente, poder, orgao, exercicio)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        files = os.listdir('data/siconfi/tmp')
        for f in files:
            shutil.move('data/siconfi/tmp/'+f, dir_path)

    def selectDropDown(self, dropdown_label, opt_label):
        elem1 = self.driver.find_element_by_id(dropdown_label)
        elem1.click()
        time.sleep(2)   
        elem2 = self.driver.find_element_by_id("{}_panel".format(dropdown_label))
        opt = self.driver.find_element_by_xpath('//li[@data-label="{}"]'.format(opt_label))
        opt.click()

    def getDropDownOpts(self, dropdown_label):
        elem = self.driver.find_element_by_id("{}_input".format(dropdown_label))
        opts = []
        for option in elem.find_elements_by_tag_name('option'):
            opts.append(option.get_attribute('text'))
        return opts[1:]

    def setTextInput(self, label, value):
        elem = self.driver.find_element_by_id("{}_input".format(label))
        elem.clear()
        elem.send_keys(value)
        time.sleep(5)
        elem.send_keys(Keys.RETURN)

    def getautoCompleteOpts(self, label):
        keys = 'aeiou'
        opts = []
        for key in keys:
            elem = self.driver.find_element_by_id("{}_input".format(label))
            elem.clear()
            elem.send_keys(key)
            time.sleep(1)
            elem2 = self.driver.find_element_by_id("{}_panel".format(label))
            for option in elem2.find_elements_by_tag_name('ul')[0].find_elements_by_tag_name('li'):
                opts.append(option.get_attribute("data-item-label"))
        return list(set(opts))

    def selectEsfera(self, label):
        return self.selectDropDown("formDeclaracao:esferaSelect",label)
    
    def getEsferaOptions(self):
        return self.getDropDownOpts("formDeclaracao:esferaSelect")

    def selectEstado(self, label):
        return self.selectDropDown("formDeclaracao:estado",label)
    
    def getEstadoOptions(self):
        return self.getDropDownOpts("formDeclaracao:estado")

    def selectEnte(self, value):
        return self.setTextInput("formDeclaracao:enteSelect", value)

    def getEnteOpts(self):
        return self.getautoCompleteOpts("formDeclaracao:enteSelect")

    def selectPoder(self, label):
        return self.selectDropDown("formDeclaracao:poderSelect",label)
    
    def getPoderOptions(self):
        self.driver.find_element_by_id("formDeclaracao:poderSelect").click()
        return self.getDropDownOpts("formDeclaracao:poderSelect")

    def selectOrgao(self, value):
        return self.setTextInput("formDeclaracao:orgaoSelect", value)

    def getOrgaoOpts(self):
        return self.getautoCompleteOpts("formDeclaracao:orgaoSelect")

    def selectExercicio(self, label):
        return self.selectDropDown("formDeclaracao:exercicio",label)
    
    def getExercicioOptions(self):
        self.driver.find_element_by_id("formDeclaracao:exercicio").click()
        return self.getDropDownOpts("formDeclaracao:exercicio")

    def saveCaptchaImage(self):
        img = self.driver.find_element_by_id('formDeclaracao:captcha:captchaImage')
        src = img.get_attribute('src')
        urllib.request.urlretrieve(src, "captcha.png")

    def inputCatcha(self, text):
        elem = self.driver.find_element_by_id("formDeclaracao:captcha:input-captcha")
        elem.send_keys(text)
        elem = self.driver.find_element_by_id("formDeclaracao:botao")
        time.sleep(1)
        elem.click()

    def downloadAllXBRL(self):
        elems = self.driver.find_elements_by_css_selector(".label.label-xbrl.has-tooltip-bottom")
        print(elems)
        for elem in elems[::-1]:
            elem.click()
            time.sleep(10)

class SiconfiAPIFetcher:

    def __init__(self, db_engine):
        self.baseUrl = 'http://apidatalake.tesouro.gov.br/ords/siconfi/tt'
        self.db_engine = db_engine

    def getItems(self, path, params, callback):
        resp = requests.get( '{}/{}'.format(self.baseUrl, path) , params=params)
        
        resp = resp.json()
        for item in resp['items']:
            callback(item)
        
        time.sleep(1)
        
        print(resp['count'])
        if resp['hasMore']:
            params['offset'] = resp['offset'] + resp['limit']
            self.getItems(path, params, callback) 


    def getEntes(self):
        def add_item(item):
            item['capital'] = int(item['capital']) == 1
            Session = sessionmaker()
            Session.configure(bind = self.db_engine)
            session = Session()
            row = Ente(**item)
            session.add(row)
            session.commit()

        self.getItems('entes',{}, add_item)


    def getMscOrcamentaria(self, **params):
            def add_item(item):
                fmt = '%Y-%m-%dT%H:%M:%SZ'
                item['data_referencia'] = datetime.strptime(item['data_referencia'], fmt)
                Session = sessionmaker()
                Session.configure(bind = self.db_engine)
                session = Session()
                row = MscOrcamentaria(**item)
                session.add(row)
                session.commit()

            self.getItems('msc_orcamentaria', params, add_item)        