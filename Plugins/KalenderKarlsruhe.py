import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

# To allow importing from parent directory
sys.path.append("../Oeffentlichkeitsarbeit-Bot")

# Adaptive import of credentials.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Import Logindaten only for type hinting (not at runtime)
    from credentials import Logindaten
else:
    from helper import Logindaten

# import helper functions
from helper import step
from my_dataclasses import Event, PluginInfo

plugininfo = PluginInfo(FRIENDLYNAME="Kalender Karlsruhe",
                        DEFAULTCATEGORY_KEY="1444", #Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={"1444": "Musik",
                         "1445": "Theater, Tanz",
                         "1443": "Literatur, Vorträge",
                         "13": "Kunst, Ausstellungen",
                         "10": "Architektur, Baukultur",
                         "450664": "Wirtschaft, Wissenschaft",
                         "7": "Messen, Kongresse",
                         "6": "Stadtleben",
                         "14": "Sport"})

def run(details: Event, credentials: Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get('https://kalender.karlsruhe.de/db/iface/termin-neu')

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cn-decline"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email")))
    time.sleep(1)


    step("Einloggen")
    email_field = driver.find_element(By.NAME, "email")
    email_field.send_keys(credentials.KALENDERKARLSRUHE_EMAIL)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(credentials.KALENDERKARLSRUHE_PASSWORD)

    driver.find_element(By.ID, "reformloginmail$").click()

    step("Lädt Seite...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reform")))

    step("Kategorie")
    Select(driver.find_element(By.ID, "reformField1")).select_by_value(details.AUSGEWÄHLTE_KATEGORIE[plugins.index(sys.modules[__name__])])

    step("Name der Veranstaltung")
    driver.find_element(By.ID, "reformField2").send_keys(details.NAME)

    step("Unterüberschrift der Veranstaltung")
    driver.find_element(By.ID, "reformField3").send_keys(details.UNTERÜBERSCHRIFT)

    step("Beschreibung der Veranstaltung")
    driver.find_element(By.ID, "reformField4").send_keys(details.BESCHREIBUNG)

    step("Beginn der Veranstaltung: Datum")
    driver.find_element(By.ID, "reformField5-dt").send_keys(details.BEGINN.strftime("%Y-%m-%d"))

    step("Beginn der Veranstaltung: Uhrzeit")
    driver.find_element(By.ID, "reformField5-tm").send_keys(details.BEGINN.strftime("%H:%M"))

    step("Ende der Veranstaltung: Datum")
    driver.find_element(By.ID, "reformField6-dt").send_keys(details.ENDE.strftime("%Y-%m-%d"))

    step("Ende der Veranstaltung: Uhrzeit")
    driver.find_element(By.ID, "reformField6-tm").send_keys(details.ENDE.strftime("%H:%M"))

    step("Veranstalungsort")
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.TAG_NAME, "input").send_keys("Z10" + Keys.TAB)

    step("Veranstalter")
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.TAG_NAME, "input").send_keys("Studentenzentrum Z10 e.V." + Keys.TAB)

    step("Link")
    driver.find_element(By.ID, "reformField10").send_keys(details.LINK)

    step("Bild")
    driver.find_element(By.ID, "reformField12").send_keys(details.BILD_DATEIPFAD)


    step("Erstellen")
    driver.find_element(By.ID, "reformcreate$").click()