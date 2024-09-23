from dataclasses import dataclass
from os.path import abspath
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from credentials import _Logindaten
import KalenderKarlsruhe

from os.path import abspath

@dataclass
class Veranstaltungsdetails:
    VERANSTALTUNG_NAME: str 
    VERANSTALTUNG_UNTERÜBERSCHRIFT: str 
    VERANSTALTUNG_BESCHREIBUNG: str  # Optional
    VERANSTALTUNG_BEGINN_DATUM: str # Format: yyyy-mm-dd
    VERANSTALTUNG_BEGINN_ZEIT: str # Format: hh:mm
    VERANSTALTUNG_ENDE_DATUM: str = "" # Format: yyyy-mm-dd
    VERANSTALTUNG_ENDE_ZEIT: str = "" # Format: hh:mm
    VERANSTALTUNG_BILD_DATEIPFAD: str = abspath("image.jpg")
    VERANSTALTUNG_LINK: str = "https://z10.info"
    VERANSTALTUNG_BEREICH: str = "1444" # Optional: #1444 = Musik
                                                    #1445 = Theater, Tanz
                                                    #1443 = Literatur, Vorträge
                                                    #13 = Kunst, Ausstellungen
                                                    #10 = Architektur, Baukultur
                                                    #450664 = Wirtschaft, Wissenschaft
                                                    #7 = Messen, Kongresse
                                                    #6 = Stadtleben
                                                    #14 = Sport

if __name__ == "__main__":
    
    details = Veranstaltungsdetails(VERANSTALTUNG_NAME = "Test-Event", 
                                    VERANSTALTUNG_UNTERÜBERSCHRIFT = "Dies ist die Unterüberschrift",
                                    VERANSTALTUNG_BESCHREIBUNG = "Dies ist eine Test-Veranstaltung des Z10 e.V. zum Testen des Veranstaltungskalenders Karlsruhe", # Optional
                                    VERANSTALTUNG_BEGINN_DATUM = "2024-10-31", # Format: yyyy-mm-dd
                                    VERANSTALTUNG_BEGINN_ZEIT = "21:00", # Format: hh:mm
                                    VERANSTALTUNG_ENDE_DATUM = "", # Format: yyyy-mm-dd
                                    VERANSTALTUNG_ENDE_ZEIT = "", # Format: hh:mm
                                    VERANSTALTUNG_BILD_DATEIPFAD = abspath("image.jpg"),
                                    VERANSTALTUNG_LINK = "https://z10.info",
                                    VERANSTALTUNG_BEREICH = "1444") # Optional: Musik
    
    options = Options()
    #options.add_argument("--headless")

    driver = Firefox(options=options)
    
    # Import login credentials
    credentials = _Logindaten()
    
    print(KalenderKarlsruhe.run(details, credentials, driver))
    
    driver.quit()