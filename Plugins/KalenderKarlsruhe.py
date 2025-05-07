from dataclasses import dataclass
import sys
import time
import ttkbootstrap as ttk
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

# import helper functions
from my_dataclasses import Event
from plugin import Plugin, PluginInfo
from publish import Publish, Logindaten
    
@dataclass
class KalenderKarlsruhe(Plugin):
    def __init__(self):
        
        self.plugininfo = PluginInfo(FRIENDLYNAME="Kalender Karlsruhe",
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
        
        super().__init__(self.plugininfo)
    
    def start(self, driver: Firefox, credentials: Logindaten, publisher: Publish):
        self.driver = driver
        self.publisher = publisher
        self.pluginindex = self.publisher.pluginlist.index(self)
        
        driver.get('https://kalender.karlsruhe.de/db/iface/termin-neu')

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cn-decline"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email")))
        time.sleep(1)

        self.step("Einloggen", "All")
        email_field = driver.find_element(By.NAME, "email")
        email_field.send_keys(credentials.KALENDERKARLSRUHE_EMAIL)

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(credentials.KALENDERKARLSRUHE_PASSWORD)

        driver.find_element(By.ID, "reformloginmail$").click()
    
    def publish_events(self, driver: Firefox, eventlist: list[Event]):
        for event in eventlist:
            self.step("Neues Event eröffnen", event)
            driver.get('https://kalender.karlsruhe.de/db/iface/termin-neu')
            
            self.step("Kategorie", event)
            Select(driver.find_element(By.ID, "reformField1")).select_by_value(event.AUSGEWÄHLTE_KATEGORIE[self.pluginindex]) ##TODO: is the pluginindex correctly set and the selected categories added in the correct order?

            self.step("Name der Veranstaltung", event)
            driver.find_element(By.ID, "reformField2").send_keys(event.NAME)

            self.step("Unterüberschrift der Veranstaltung", event)
            driver.find_element(By.ID, "reformField3").send_keys(event.UNTERÜBERSCHRIFT)

            self.step("Beschreibung der Veranstaltung", event)
            driver.find_element(By.ID, "reformField4").send_keys(event.BESCHREIBUNG)

            self.step("Beginn der Veranstaltung: Datum", event)
            driver.find_element(By.ID, "reformField5-dt").send_keys(event.BEGINN.strftime("%Y-%m-%d"))

            self.step("Beginn der Veranstaltung: Uhrzeit", event)
            driver.find_element(By.ID, "reformField5-tm").send_keys(event.BEGINN.strftime("%H:%M"))

            self.step("Ende der Veranstaltung: Datum", event)
            driver.find_element(By.ID, "reformField6-dt").send_keys(event.ENDE.strftime("%Y-%m-%d"))

            self.step("Ende der Veranstaltung: Uhrzeit", event)
            driver.find_element(By.ID, "reformField6-tm").send_keys(event.ENDE.strftime("%H:%M"))

            self.step("Veranstalungsort", event)
            driver.find_element(By.ID, "reformField8_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
            driver.find_element(By.ID, "reformField8_chosen").find_element(By.TAG_NAME, "input").send_keys("Z10" + Keys.TAB)

            self.step("Veranstalter", event)
            driver.find_element(By.ID, "reformField9_chosen").find_element(By.CLASS_NAME, "chosen-single").click()
            driver.find_element(By.ID, "reformField9_chosen").find_element(By.TAG_NAME, "input").send_keys("Studentenzentrum Z10 e.V." + Keys.TAB)

            self.step("Link", event)
            driver.find_element(By.ID, "reformField10").send_keys(event.LINK)

            self.step("Bild", event)
            driver.find_element(By.ID, "reformField12").send_keys(event.BILD_DATEIPFAD)

            self.step("Bestätigen", event)
            #driver.find_element(By.ID, "reformcreate$").click()
            
            self.error(event)
            
            time.sleep(5)
            
            self.success(event)

            self.step("Warte auf Erstellen", event)
            WebDriverWait(driver, 60).until(lambda driver: "/preview" in driver.current_url)
    
    def stop(driver: Firefox):
        pass