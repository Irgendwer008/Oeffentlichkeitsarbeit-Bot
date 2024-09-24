from datetime import datetime
import time
import locale
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from helper import Veranstaltungsdetails, round_nearest_30min
from credentials import _Logindaten

def run(details: Veranstaltungsdetails, credentials: _Logindaten, driver: Firefox):
    
    
    # Open Website
    
    driver.get("https://gewerbe.nebenan.de/businesses/190915/feed")
    
    
    # Decline cookies
    
    WebDriverWait(driver, 3).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[title="SP Consent message"]')))
    
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".message-component.message-button.no-children.focusable.sp_choice_type_13"))).click()
    
    driver.switch_to.default_content()
    
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, "email")))


    # Login
    
    email_field = driver.find_element(By.NAME, "email")
    email_field.send_keys(credentials.NEBENANDE_EMAIL)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(credentials.NEBENANDE_PASSWORD)

    driver.find_element(By.CLASS_NAME, "ui-button-primary").click()   
    
     
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    
    time.sleep(1)


    # Open dialogue
    
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(driver.find_elements(By.CLASS_NAME, "dYCQE7YIdld3Hla7RBuT")[2])).click()
    
    
    # Filling out Form
    
    ## Titel und Veranstaltungsort
    elements = driver.find_elements(By.TAG_NAME, "input")
    elements[0].send_keys(details.VERANSTALTUNG_NAME)
    elements[1].send_keys(details.VERANSTALTUNG_ORT)
    
    ## Beginn: Tag
    elements[2].click()
        
    locale.setlocale(locale.LC_TIME, "de_DE.UTF8")    
    
    while (driver.find_element(By.CLASS_NAME, "c-picker-controls-label").text != details.VERANSTALTUNG_BEGINN.strftime("%B %Y")):
        driver.find_element(By.CSS_SELECTOR, ".c-picker-controls-next.icon-arrow_right").click()
        
    for datebutton in driver.find_elements(By.TAG_NAME, "td"):
        try:
            datebutton.find_element(By.XPATH, "//span[text()='" + str(details.VERANSTALTUNG_BEGINN.day) + "']").click()
            break
        except NoSuchElementException:
            pass
    
    ## Beginn: Uhrzeit
    Select(driver.find_element(By.NAME, "starttime_0")).select_by_visible_text(round_nearest_30min(details.VERANSTALTUNG_BEGINN).strftime("%H:%M"))
    
    ## Ende
    if (details.VERANSTALTUNG_ENDE is not None):
        
        driver.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div/article/div/div/article/section/form/article[2]/ul/li/span").click()
        driver.find_elements(By.TAG_NAME, "input")[3].click()
        
        ## Ende: Tag 
        
        while (driver.find_element(By.CLASS_NAME, "c-picker-controls-label").text != details.VERANSTALTUNG_BEGINN.strftime("%B %Y")):
            driver.find_element(By.CSS_SELECTOR, ".c-picker-controls-next.icon-arrow_right").click()
            
        for datebutton in driver.find_elements(By.TAG_NAME, "td"):
            try:
                datebutton.find_element(By.XPATH, "//span[text()='" + str(details.VERANSTALTUNG_BEGINN.day) + "']").click()
                break
            except NoSuchElementException:
                pass
        
        ## Ende: Uhrzeit
        Select(driver.find_element(By.NAME, "endtime_0")).select_by_visible_text(round_nearest_30min(details.VERANSTALTUNG_ENDE, True).strftime("%H:%M"))    
    
    ## Beschreibung
    driver.find_element(By.TAG_NAME, "textarea").send_keys(details.VERANSTALTUNG_BESCHREIBUNG)
    
    ## Bild
    driver.find_element(By.CLASS_NAME, "c-file_picker-input").send_keys(details.VERANSTALTUNG_BILD_DATEIPFAD)
    time.sleep(1)
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/div/div/div/article/footer/span[1]"))).click()
        
    ## Kategorie
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div/article/div/div/article/section/form/div[5]/div/div/div"))).click()
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/div/div/div/article/div/article/ul/li[3]"))).click()
        
    ## Submit
    driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
        
    time.sleep(60)

    return