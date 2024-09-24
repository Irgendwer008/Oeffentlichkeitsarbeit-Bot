import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from helper import Veranstaltungsdetails
from credentials import _Logindaten



def run(details: Veranstaltungsdetails, credentials: _Logindaten, driver: Firefox):
    
    driver.get('https://kalender.karlsruhe.de/db/iface/termin-neu')


    # Decline Cookies
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, "cn-decline"))).click()
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, "email")))
    time.sleep(1)


    # Login
    
    email_field = driver.find_element(By.NAME, "email")
    email_field.send_keys(credentials.KALENDERKARLSRUHE_EMAIL)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(credentials.KALENDERKARLSRUHE_PASSWORD)

    driver.find_element(By.ID, "reformloginmail$").click()

    # Waiting for page loading
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "reform")))
    print(driver.current_url)


    # Filling out form

    ## Bereich
    Select(driver.find_element(By.ID, "reformField1")).select_by_value(details.VERANSTALTUNG_BEREICH)

    ## Name der Veranstaltung
    driver.find_element(By.ID, "reformField2").send_keys(details.VERANSTALTUNG_NAME)

    ## Unterüberschrift der Veranstaltung
    driver.find_element(By.ID, "reformField3").send_keys(details.VERANSTALTUNG_UNTERÜBERSCHRIFT)

    if (details.VERANSTALTUNG_BESCHREIBUNG != ""):
        ## Beschreibung der Veranstaltung
        driver.find_element(By.ID, "reformField4").send_keys(details.VERANSTALTUNG_BESCHREIBUNG)

    ## Beginn der Veranstaltung: Datum
    driver.find_element(By.ID, "reformField5-dt").send_keys(details.VERANSTALTUNG_BEGINN_DATUM)

    ## Beginn der Veranstaltung: Uhrzeit
    driver.find_element(By.ID, "reformField5-tm").send_keys(details.VERANSTALTUNG_BEGINN_ZEIT)

    if (details.VERANSTALTUNG_ENDE_DATUM != "" and details.VERANSTALTUNG_ENDE_ZEIT != ""):
        ## Ende der Veranstaltung: Datum
        driver.find_element(By.ID, "reformField6-dt").send_keys(details.VERANSTALTUNG_ENDE_DATUM)

        ## Ende der Veranstaltung: Uhrzeit
        driver.find_element(By.ID, "reformField6-tm").send_keys(details.VERANSTALTUNG_ENDE_ZEIT)

    ## Veranstalungsort
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField8_chosen").find_element(By.TAG_NAME, "input").send_keys("Z10" + Keys.TAB)

    ## Veranstalter
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
    driver.find_element(By.ID, "reformField9_chosen").find_element(By.TAG_NAME, "input").send_keys("Studentenzentrum Z10 e.V." + Keys.TAB)

    ## Webadresse
    driver.find_element(By.ID, "reformField10").send_keys(details.VERANSTALTUNG_LINK)

    ## Bild
    driver.find_element(By.ID, "reformField12").send_keys(details.VERANSTALTUNG_BILD_DATEIPFAD)


    # Send form
    driver.find_element(By.ID, "reformcreate$").click()

    time.sleep(1)


    # check for error messages
    try:
        return driver.find_element(By.CLASS_NAME, "alert").get_attribute("innerHTML")
    except NoSuchElementException:
        return "Modul: KalenderKarlsruhe: Fehler!\n"