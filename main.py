from datetime import datetime
from os.path import abspath
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

from helper import Veranstaltungsdetails
from credentials import _Logindaten

import KalenderKarlsruhe
import Nebenande

from os.path import abspath

if __name__ == "__main__":
    
    details = Veranstaltungsdetails(VERANSTALTUNG_NAME = "Test-Event", 
                                    VERANSTALTUNG_UNTERÜBERSCHRIFT = "Dies ist die Unterüberschrift",
                                    VERANSTALTUNG_BESCHREIBUNG = "Dies ist eine Test-Veranstaltung des Z10 e.V. zum Testen des Veranstaltungskalenders Karlsruhe", # Optional
                                    VERANSTALTUNG_BEGINN_DATUM = "2024-10-31",
                                    VERANSTALTUNG_BEGINN_ZEIT = "21:00",
                                    VERANSTALTUNG_ENDE_DATUM = "2024-11-01",
                                    VERANSTALTUNG_ENDE_ZEIT = "01:30",
                                    VERANSTALTUNG_BILD_DATEIPFAD = abspath("image.jpg"))
    
    #TODO: check for valid inputs: future date, locale (datepicker nebenan.de)
    #TODO: Make Nebenan.de time selection functional
    #TODO: Make Nebenan.de category functional
    #TODO: Notify that time for Nebenan.de will be cut to nearest half hour
            
    options = Options()
    #options.add_argument("--headless")

    driver = Firefox(options=options)
    
    # Import login credentials
    credentials = _Logindaten()
    
    try:
        KalenderKarlsruhe.run(details, credentials, driver)
        Nebenande.run(details, credentials, driver)
    except TimeoutException:
        print("Timeout while loading a page")
    
    driver.quit()