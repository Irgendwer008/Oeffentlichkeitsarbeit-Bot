from dataclasses import dataclass
from datetime import datetime
from os.path import exists
from os.path import abspath
from os.path import expanduser
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

from credentials import _Logindaten
from helper import Veranstaltungsdetails, round_nearest_30min

import KalenderKarlsruhe
import Nebenande

from os.path import abspath

if __name__ == "__main__":
    
    try:
    
        print("######################")
        print("#                    #")
        print("#  Z10 Autouploader  #")
        print("#                    #")
        print("######################")
        
        # Name
        name = ""
        while name == "":
            name = input("\n# Wie lautet der Titel der Veranstaltung?: ")
        
        # Unterüberschrift
        unterüberschrift = ""
        while unterüberschrift == "":
            unterüberschrift = input("\n# Wie lautet die Unterüberschrift der Veranstaltung?: ")
        
        # Beschreibung
        beschreibung = ""
        while beschreibung == "":
            beschreibung = input("\n# Wie lautet die Beschreibung der Veranstaltung?: ")
        
        # Veranstaltungsbegin
        while (True):
            try:
                veranstaltungsbeginn = datetime.strptime(input("\n# Wann beginnt die Veranstaltung? (Format: 01.02.2024 17:42): "), "%d.%m.%Y %H:%M")
                if veranstaltungsbeginn < datetime.now():
                    raise Exception
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print("\n!! Deine Eingabe hat das falsche Format oder liegt in der Vergangenheit! Bitte gib Datum und Uhrzeit anhand des Beispiels an.")
        
        # Veranstaltungsende
        veranstaltungsende = None
        
        while (True):
            
            string = input("\n# Wann endet die Veranstaltung?\nLasse dieses Feld frei, wenn deine Veranstaltung keine bestimmte Endzeit hat.\n(Format: 01.02.2024 17:42): ")
                        
            if string == "":
                break
            
            try:
                veranstaltungsende = datetime.strptime(string, "%d.%m.%Y %H:%M")
                print(veranstaltungsende, veranstaltungsbeginn)
                #if veranstaltungsende < veranstaltungsbeginn:
                #    raise Exception
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print("\n!! Deine Eingabe \"" + string + "\" hat das falsche Format oder liegt vor dem Beginn der Veranstaltung! Bitte gib Datum und Uhrzeit anhand des Beispiels an oder lasse dieses Feld frei, wenn du keine Endzeit angeben möchtest.")
        
        if veranstaltungsbeginn.minute % 30 != 0:
            print("\ni Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die Angegebenen Uhrzeiten werden gerundet auf " + round_nearest_30min(veranstaltungsbeginn).strftime("%H:%M"), end="")

            if veranstaltungsende is not None and veranstaltungsende.minute % 30 != 0:
                print(" bzw. " + round_nearest_30min(veranstaltungsende, True).strftime("%H:%M"), end="")
            
            print("")
        
        
        # Bild
        filepath = input("\n# Wie lautet der Dateipfad zum Bild der Veranstaltung?: ")
            
        while not exists(filepath) or not (filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".gif")):
            filepath = input("\n!! Bitte nenne einen existierenden dateipfad: ")
            
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet. Die Veranstaltung wird nicht veröffentlicht.\n")
        exit()
    
    # Done
    details = Veranstaltungsdetails(VERANSTALTUNG_NAME = name, 
                                    VERANSTALTUNG_UNTERÜBERSCHRIFT = unterüberschrift,
                                    VERANSTALTUNG_BESCHREIBUNG = beschreibung,
                                    VERANSTALTUNG_BEGINN = veranstaltungsbeginn,
                                    VERANSTALTUNG_ENDE = veranstaltungsende,
                                    VERANSTALTUNG_BILD_DATEIPFAD = abspath(filepath))
    
    #TODO: check for valid values: locale (datepicker nebenan.de)
    #TODO: Make Nebenan.de category functional
    #TODO: Make "Eine Z10 Veranstaltung" the default Unterüberschrift
            
    options = Options()
    #options.add_argument("--headless")

    driver = Firefox(options=options)
    
    # Import login credentials
    credentials = _Logindaten()
    
    try:
        KalenderKarlsruhe.run(details, credentials, driver)
        Nebenande.run(details, credentials, driver)
        driver.quit()
    except TimeoutException:
        print("Timeout while loading a page")
    except KeyboardInterrupt:
        print("\n\n!!Achtung!! Das Programm wurde während des Hochladens unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, da die Veranstaltung nirgendwo, teilweise oder bereits überall veröffentlicht sein kann!\n")