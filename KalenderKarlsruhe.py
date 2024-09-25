import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from helper import Veranstaltungsdetails, PluginInfo
from credentials import _Logindaten

plugininfo = PluginInfo(FRIENDLYNAME="Kalender Karlsruhe",
                        DEFAULTCATEGORY_KEY="1444", # Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={"1444": "Musik",
                         "1445": "Theater, Tanz",
                         "1443": "Literatur, Vorträge",
                         "13": "Kunst, Ausstellungen",
                         "10": "Architektur, Baukultur",
                         "450664": "Wirtschaft, Wissenschaft",
                         "7": "Messen, Kongresse",
                         "6": "Stadtleben",
                         "14": "Sport"})

def run(details: Veranstaltungsdetails, credentials: _Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get('https://kalender.karlsruhe.de/db/iface/termin-neu')

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cn-decline"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email")))
    time.sleep(1)


    # Login
    
    email_field = driver.find_element(By.NAME, "email")
    email_field.send_keys(credentials.KALENDERKARLSRUHE_EMAIL)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(credentials.KALENDERKARLSRUHE_PASSWORD)

    driver.find_element(By.ID, "reformloginmail$").click()

    # Waiting for page loading
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reform")))
    

    # Filling out form

    ## Kategorie
    Select(driver.find_element(By.ID, "reformField1")).select_by_value(details.AUSGEWÄHLTE_KATEGORIE[plugins.index(sys.modules[__name__])])

    ## Name der Veranstaltung
    driver.find_element(By.ID, "reformField2").send_keys(details.NAME)

    ## Unterüberschrift der Veranstaltung
    driver.find_element(By.ID, "reformField3").send_keys(details.UNTERÜBERSCHRIFT)

    if (details.BESCHREIBUNG != ""):
        ## Beschreibung der Veranstaltung
        driver.find_element(By.ID, "reformField4").send_keys(details.BESCHREIBUNG)

    ## Beginn der Veranstaltung: Datum
    driver.find_element(By.ID, "reformField5-dt").send_keys(details.BEGINN.strftime("%Y-%m-%d"))

    ## Beginn der Veranstaltung: Uhrzeit
    driver.find_element(By.ID, "reformField5-tm").send_keys(details.BEGINN.strftime("%H:%M"))

    if (details.ENDE is not None):
        ## Ende der Veranstaltung: Datum
        driver.find_element(By.ID, "reformField6-dt").send_keys(details.ENDE.strftime("%Y-%m-%d"))

        ## Ende der Veranstaltung: Uhrzeit
        driver.find_element(By.ID, "reformField6-tm").send_keys(details.ENDE.strftime("%H:%M"))

    ## Veranstalungsort
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.TAG_NAME, "input").send_keys("Z10" + Keys.TAB)

    ## Veranstalter
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.TAG_NAME, "input").send_keys("Studentenzentrum Z10 e.V." + Keys.TAB)

    ## Webadresse
    driver.find_element(By.ID, "reformField10").send_keys(details.LINK)

    ## Bild
    driver.find_element(By.ID, "reformField12").send_keys(details.BILD_DATEIPFAD)


    # Send form
    driver.find_element(By.ID, "reformcreate$").click()