import sys
import time
import locale
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

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
from helper import my_dataclasses, step, round_nearest_30min
from my_dataclasses import Event, PluginInfo

plugininfo = PluginInfo(FRIENDLYNAME="Nebenan.de",
                        DEFAULTCATEGORY_KEY="2", # Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={"0": "Kennenlernen & Stammtische",
                         "1": "Bildung & Erfahrung",
                         "2": "Kunst, Kultur & Musik",
                         "3": "Märkte & Flohmärkte",
                         "4": "Familien & Kinder",
                         "5": "Essen & Trinken",
                         "6": "Feste & Feiern",
                         "7": "Lokales Engagement",
                         "8": "Gestalten & Heimwerken",
                         "9": "Gesundheit & Wellness",
                         "10": "Sport & Bewegung",
                         "11": "Umwelt & Nachhaltigkeit",
                         "12": "Teilen, Tauschen, Reparieren",
                         "13": "Viertel verschönern",
                         "14": "Ausflüge",
                         "15": "Sonstiges"})

def run(details: Event, credentials: Logindaten, plugins: list[str], driver: Firefox):
    
    step("Website öffnen")
    driver.get("https://gewerbe.nebenan.de/businesses/190915/feed")
    
    
    step("Cookies ablehnen")
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[title="SP Consent message"]')))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".message-component.message-button.no-children.focusable.sp_choice_type_13"))).click()
    driver.switch_to.default_content()
    


    step("Einloggen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(credentials.NEBENANDE_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(credentials.NEBENANDE_PASSWORD)
    driver.find_element(By.CLASS_NAME, "ui-button-primary").click()   
    
     
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    time.sleep(1)


    step("Formular öffnen")    
    driver.get("https://gewerbe.nebenan.de/businesses/190915/feed") # otherwise doesn't wait long enough
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Veranstaltung')]/ancestor::article/ancestor::li/article")))
        
    driver.find_element(By.XPATH, "//strong[contains(text(), 'Veranstaltung')]/ancestor::article/ancestor::li/article").click()
    
    step("Titel und Veranstaltungsort")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        driver.find_element(By.NAME, "subject"))).send_keys(details.NAME)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Ort der Veranstaltung"]').send_keys(details.STRASSE)
    
    step("Beginn: Tag")
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Tag"]').click()
        
    locale.setlocale(locale.LC_TIME, "de_DE.UTF8")    
    
    while (driver.find_element(By.CLASS_NAME, "c-picker-controls-label").text != details.BEGINN.strftime("%B %Y")):
        driver.find_element(By.CSS_SELECTOR, ".c-picker-controls-next.icon-arrow_right").click()
        
    for datebutton in driver.find_elements(By.TAG_NAME, "td"):
        try:
            datebutton.find_element(By.XPATH, "//span[text()='" + str(details.BEGINN.day) + "']").click()
            break
        except NoSuchElementException:
            pass
    
    step("Beginn: Uhrzeit")
    Select(driver.find_element(By.NAME, "starttime_0")).select_by_visible_text(round_nearest_30min(details.BEGINN).strftime("%H:%M"))
    
    step("Ende")
    driver.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div/article/div/div/article/section/form/article[2]/ul/li/span").click()
    driver.find_elements(By.TAG_NAME, "input")[3].click()
    
    step("Ende: Tag")
    
    while (driver.find_element(By.CLASS_NAME, "c-picker-controls-label").text != details.BEGINN.strftime("%B %Y")):
        driver.find_element(By.CSS_SELECTOR, ".c-picker-controls-next.icon-arrow_right").click()
        
    for datebutton in driver.find_elements(By.TAG_NAME, "td"):
        try:
            datebutton.find_element(By.XPATH, "//span[text()='" + str(details.BEGINN.day) + "']").click()
            break
        except NoSuchElementException:
            pass
    
    step("Ende: Uhrzeit")
    Select(driver.find_element(By.NAME, "endtime_0")).select_by_visible_text(round_nearest_30min(details.ENDE, True).strftime("%H:%M"))    
    
    step("Beschreibung")
    driver.find_element(By.CSS_SELECTOR, "textarea[placeholder=\"Deine Veranstaltungsbeschreibung\"]").send_keys(details.BESCHREIBUNG)
    
    step("Bild")
    driver.find_element(By.CLASS_NAME, "c-file_picker-input").send_keys(details.BILD_DATEIPFAD)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/div/div/div/article/footer/span[1]"))).click()
        
    step("Kategorie")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div/article/div/div/article/section/form/div[5]/div/div/div"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/div/div/div/article/div/article/ul/li[" + str(int(details.AUSGEWÄHLTE_KATEGORIE[plugins.index(sys.modules[__name__])]) + 1) + "]"))).click()
            
    step("Speichern")
    #driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
    time.sleep(600)