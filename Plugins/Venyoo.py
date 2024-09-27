from datetime import datetime
import time
import locale
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys

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
from helper import Veranstaltungsdetails, PluginInfo, step
from Plugins import Z10Website

plugininfo = PluginInfo(FRIENDLYNAME="Venyoo",
                        DEFAULTCATEGORY_KEY=None, # Set to None (not "None" :D), if this platform doesn't use categories
                        KATEGORIEN={})



def run(details: Veranstaltungsdetails, credentials: Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get("https://venyoo.de/home")
    
    step("Einloggen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "email"))).send_keys(credentials.VENYOO_USERNAME)
    driver.find_element(By.ID, "password").send_keys(credentials.VENYOO_PASSWORD)
    driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[1]/form/div[3]/button').click()
    
    step("Veranstaltung eintragen")
    driver.get("https://venyoo.de/home/event/create")
    
    step("Titel einfügen")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "name"))).send_keys(details.NAME)
    
    
    step("Datum angeben")        
    driver.find_element(By.NAME, "eventdates[new-1][startdate]").click()
    locale.setlocale(locale.LC_TIME, "de_DE.UTF8") 
             
    step("Datum angeben: Jahr")  
    while (driver.find_element(By.XPATH, "(//div[@class='dw-li dw-v dw-sel'])[3]/div").text != str(details.BEGINN.year)):
        driver.find_elements(By.CLASS_NAME, "mbsc-ic-arrow-down6")[2].click()
        
    step("Datum angeben: Monat")  
    while (driver.find_element(By.XPATH, "(//div[@class='dw-li dw-v dw-sel'])[2]/div").text != datetime.strftime(details.BEGINN, "%B")):
        driver.find_elements(By.CLASS_NAME, "mbsc-ic-arrow-down6")[1].click()
    
    step("Datum angeben: Tag")  
    while (driver.find_element(By.XPATH, "(//div[@class='dw-li dw-v dw-sel'])[1]/div").text[3:] != str(details.BEGINN.day)):
        driver.find_elements(By.CLASS_NAME, "mbsc-ic-arrow-down6")[0].click()
        
    step("Datum angeben: Bestätigen") 
    time.sleep(0.1)
    driver.find_element(By.CSS_SELECTOR, "div[role=\"button\"]").click()
    
    
    step("Uhrzeit angeben")        
    driver.find_element(By.NAME, "eventdates[new-1][starttime]").click()
        
    step("Uhrzeit angeben: Stunde")  
    while (driver.find_element(By.XPATH, "(//div[@class='dw-li dw-v dw-sel'])[1]/div").text != details.BEGINN.strftime("%H")):
        driver.find_elements(By.CLASS_NAME, "mbsc-ic-arrow-down6")[0].click()
    
    step("Uhrzeit angeben: Minute")  
    while (driver.find_element(By.XPATH, "(//div[@class='dw-li dw-v dw-sel'])[2]/div").text != details.BEGINN.strftime("%M")):
        driver.find_elements(By.CLASS_NAME, "mbsc-ic-arrow-down6")[1].click()
        
    step("Uhrzeit angeben: Bestätigen")
    time.sleep(0.1)
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div[4]/div[1]/div").click()
    
    step("Bild angeben")
    driver.find_element(By.ID, "fileupload").send_keys(details.BILD_DATEIPFAD)
        
    step("Veranstaltungsort angeben") 
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "venue"))).send_keys(details.LOCATION)
        
    step("Addresse angeben") 
    driver.find_element(By.ID, "address").send_keys(details.STRASSE)
        
    step("Stadt angeben") 
    driver.find_element(By.ID, "city").send_keys(details.STADT)
        
    step("PLZ angeben") 
    driver.find_element(By.ID, "zip").send_keys(details.PLZ)
        
    step("Beschreibung angeben") 
    driver.find_element(By.ID, "description").send_keys(details.BESCHREIBUNG)
        
    try:
        step("Kategorie angeben")
        driver.find_elements(By.NAME, "tag[]")[0].send_keys(Z10Website.plugininfo.KATEGORIEN[Z10Website.plugininfo.DEFAULTCATEGORY_KEY])
    except NameError:
        pass
        
    step("Warte auf Hochladen des Bildes")
    while not "image-set" in driver.find_element(By.XPATH, "//div[@class='upload_item_image']").get_attribute("style") and driver.find_element(By.CLASS_NAME, "upload_item_name").text != "error":
        time.sleep(0.1)
        if driver.find_element(By.CLASS_NAME, "upload_item_name").text == "error":
            print("\n\nEs gab ein Problem beim Hochladen des Bildes! Vermutlich ist es zu groß oder ein falsches Format. Veranstaltung wird ohne Bild hochgeladen\n")
    
    step("Veranstaltung speichern")
    driver.find_element(By.XPATH, '//button[@class="btn btn-success"]').click()