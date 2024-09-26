from datetime import datetime
import sys
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from helper import Veranstaltungsdetails, PluginInfo, round_nearest_30min, step
from credentials import _Logindaten

plugininfo = PluginInfo(FRIENDLYNAME="Z10 Homepage + Wiki",
                        DEFAULTCATEGORY_KEY="5", # Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={"9": "Filme",
                                    "18": "Geilster Tag des Monats",
                                    "10": "Info-Veranstaltung",
                                    "4": "Kabarett",
                                    "5": "Konzert",
                                    "12": "Krümel",
                                    "6": "Lesung",
                                    "7": "Party",
                                    "15": "Quiz",
                                    "13": "Theater"})



def run(details: Veranstaltungsdetails, credentials: _Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get("https://admin.z10.info/termine/create")
    
    step("Einloggen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(credentials.Z10_USERNAME)
    driver.find_element(By.ID, "password").send_keys(credentials.Z10_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
    
    step("Titel angeben")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "EventName"))).send_keys(details.NAME)
    
    step("Veranstaltungsbeginn angeben")
    driver.find_element(By.ID, "eventBegin").send_keys(datetime.strftime(details.BEGINN, "%m%d%Y%H%M"))

    step("Veranstaltungsende angeben")
    driver.find_element(By.ID, "eventEnd").send_keys(datetime.strftime(details.ENDE, "%m%d%Y%H%M"))
    
    step("Kategorie auswählen")
    Select(driver.find_element(By.ID, "category")).select_by_value(details.AUSGEWÄHLTE_KATEGORIE[plugins.index(sys.modules[__name__])])
    
    step("Bild einfügen")
    driver.find_element(By.ID, "image").send_keys(details.BILD_DATEIPFAD)
    
    step("Beschreibung angeben")
    textarea = driver.find_element(By.CSS_SELECTOR, "div[contenteditable=\"true\"]")
    textarea.click()
    textarea.send_keys(details.BESCHREIBUNG + Keys.TAB)
    
    step("Termin erstellen")
    driver.find_element(By.ID, "submitButton").click()