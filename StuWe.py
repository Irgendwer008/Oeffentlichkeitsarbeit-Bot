from datetime import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from helper import Veranstaltungsdetails, PluginInfo, round_nearest_30min, step
from credentials import _Logindaten

plugininfo = PluginInfo(FRIENDLYNAME="StuWe Veranstaltungskalender",
                        DEFAULTCATEGORY_KEY=None, # Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={})

def run(details: Veranstaltungsdetails, credentials: _Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get("https://www.sw-ka.de/de/")
    
    step("Sicherstellen dass Sprache DE ausgewählt ist")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[onclick="setLang(\'de\');"]'))).click()
    
    step("Login drücken")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'LOGIN')]"))).click()
    
    step("Einloggen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "auth_username"))).send_keys(credentials.STUWE_USERNAME)
    driver.find_element(By.ID, "auth_password").send_keys(credentials.STUWE_PASSWORD)
    driver.find_element(By.ID, "login").click()
    
    step("Veranstaltungskalender öffnen")
    driver.get("https://www.sw-ka.de/de/mein_account/service/veranstaltungskalender/")
        
    step("Neuen Eintrag hinzufügen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Neuen Eintrag hinzufügen')]"))).click()
        
    step("Bild einfügen")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(details.BILD_DATEIPFAD)
    
    step("Veranstaltungsbeginn angeben")
    driver.find_element(By.ID, "start_date").send_keys(datetime.strftime(details.BEGINN, "%d.%m.%Y"))

    step("Veranstaltungsende angeben")
    driver.find_element(By.ID, "end_date").send_keys(datetime.strftime(details.ENDE, "%d.%m.%Y"))

    step("Titel angeben")
    driver.find_element(By.ID, "title").send_keys(details.NAME)

    step("Beschreibung angeben")
    driver.find_element(By.ID, "content").send_keys(details.BESCHREIBUNG)

    step("Stadt angeben")
    driver.find_element(By.ID, "event_city").send_keys(details.STADT)

    step("Veranstaltungsort angeben")
    driver.find_element(By.ID, "location").send_keys(details.LOCATION)

    step("Postalische Addresse angeben")
    driver.find_element(By.ID, "address").send_keys(details.STRASSE + ", " + details.PLZ + " " +details.STADT)

    step("Vorverkaufspreis angeben")
    driver.find_element(By.ID, "vvk").send_keys("0")

    step("Abendkasse angeben")
    driver.find_element(By.ID, "ak").send_keys("0")

    step("Ermäßigtenpreis angeben")
    driver.find_element(By.ID, "em").send_keys("0")

    step("Link angeben")
    driver.find_element(By.ID, "link").send_keys(details.LINK)

    step("Vorschau öffnen")
    driver.find_element(By.ID, "save").click()

    step("Bild einfügen")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "agree2"))).click()

    step("Eintrag absenden")
    driver.find_element(By.XPATH, "//button[contains(text(), 'Eintrag absenden')]").click()
    