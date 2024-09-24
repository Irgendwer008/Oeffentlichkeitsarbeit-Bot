from datetime import datetime
from os.path import exists
from os.path import abspath
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from credentials import _Logindaten
from helper import Veranstaltungsdetails, round_nearest_30min, YES, NO
    
import KalenderKarlsruhe
import Nebenande
plugins = [KalenderKarlsruhe, Nebenande]

from os.path import abspath
    
#TODO: check for valid values: locale (datepicker nebenan.de)
#TODO: Make categories functional
#TODO: Allow choosing of which plugins to use
#TODO: Check if events where published correctly (prob takes much time :,) )
#TODO: limit text lengths: Nebenande: titel: 2 <= text <= 60, Beschreibung: 2 <= text <= 5000

def get_name() -> str:
    name = "Test"
    while name == "":
        name = input("\n# Wie lautet der Titel der Veranstaltung?: ")
    return name
        
def get_unterüberschrift() -> str:
    unterüberschrift = input("\n# Wie lautet die Unterüberschrift der Veranstaltung? (Optional, Standart ist '" + Veranstaltungsdetails.UNTERÜBERSCHRIFT + "'): ")
    if unterüberschrift == "":
        unterüberschrift = Veranstaltungsdetails.UNTERÜBERSCHRIFT
    return unterüberschrift
        
def get_beschreibung() -> str:
    beschreibung = "Dies ist eine Testbeschreibung"
    while beschreibung == "":
        beschreibung = input("\n# Wie lautet die Beschreibung der Veranstaltung?: ")
    return beschreibung

def get_beginn() -> datetime:
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
    return veranstaltungsbeginn

def get_ende(veranstaltungsbeginn) -> datetime:
    veranstaltungsende = None
    while (True):
        
        string = input("\n# Wann endet die Veranstaltung? Lasse dieses Feld frei, wenn deine Veranstaltung keine bestimmte Endzeit hat. (Format: 01.02.2024 17:42): ")
                    
        if string == "":
            break
        
        try:
            veranstaltungsende = datetime.strptime(string, "%d.%m.%Y %H:%M")
            if veranstaltungsende < veranstaltungsbeginn:
                raise Exception
            break
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print("\n!! Deine Eingabe \"" + string + "\" hat das falsche Format oder liegt vor dem Beginn der Veranstaltung! Bitte gib Datum und Uhrzeit anhand des Beispiels an oder lasse dieses Feld frei, wenn du keine Endzeit angeben möchtest.")
    return veranstaltungsende

def notify_of_rounded_times(beginn: datetime, ende: datetime):
    if beginn.minute % 30 != 0:
        print("\ni Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die Angegebenen Uhrzeiten werden gerundet auf " + round_nearest_30min(beginn).strftime("%H:%M"), end="")

        if ende is not None and ende.minute % 30 != 0:
            print(" bzw. " + round_nearest_30min(ende, True).strftime("%H:%M"), end="")
        
        print("")
    return

def get_bild() -> str:
    filepath = "image.jpg" # input("\n# Wie lautet der Dateipfad zum Bild der Veranstaltung?: ")
        
    while not exists(filepath) or not (filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".gif")):
        filepath = input("\n!! Bitte nenne einen existierenden dateipfad: ")
    return abspath(filepath)

"""
def get_single_category(index: int) -> str:
    categories = plugins[index].plugininfo
def get_kategorien() -> list[str]:
        default_categories = ""
        while True:
            default_categories = input("Sollen die Standartkategorien ("
                "Kalenderkarlsruhe: \"" + Kategorien.KALENDERKARLSRUHE[Veranstaltungsdetails.KATEGORIE_KALENDERKARLSRUHE] + "\" und "
                "Nebenan.de: \"" + Kategorien.NEBENANDE[Veranstaltungsdetails.KATEGORIE_NEBENANDE] + "\") beibehalten werden? [Y/n]")
            if default_categories in YES:
                break
            elif default_categories in NO:
                # Kalender Karlsruhe
                
                # Nebenande
                
                category_kalenderkarlsruhe = input("")
"""

if __name__ == "__main__":
    
    print("######################")
    print("#                    #")
    print("#  Z10 Autouploader  #")
    print("#                    #")
    print("######################")
    
    # Get event details
    try:
        details = Veranstaltungsdetails(NAME = get_name(), 
                                        UNTERÜBERSCHRIFT = get_unterüberschrift(),
                                        BESCHREIBUNG = get_beschreibung(),
                                        BEGINN = datetime.strptime("31.10.2024 20:00", "%d.%m.%Y %H:%M"), # get_beginn(),
                                        ENDE = datetime.strptime("31.10.2024 23:50", "%d.%m.%Y %H:%M"), # get_ende(veranstaltungsbeginn),
                                        BILD_DATEIPFAD = get_bild())  
        notify_of_rounded_times(details.BEGINN, details.ENDE)   
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet. Die Veranstaltung wurde nicht veröffentlicht.\n")
        exit()
    
    # Get login credentials
    credentials = _Logindaten
    
    # init driver
    options = Options()
    #options.add_argument("--headless")
    driver = Firefox(options=options)
    
    # Newline
    print("")
    
    # Execute all the plugins
    try:
        lastsuccesful = 0
        for plugin in plugins:
            plugin.run(details, credentials, plugins, driver)
            print("Veranstaltung erfolgreich auf " + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + " veröffentlicht.")
            lastsuccesful += 1
        driver.quit()
    except KeyboardInterrupt:
        print("\n\n!!Achtung!! Das Programm wurde vom Benutzer während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung bereits veröffentlicht sein kann oder nicht!\n")
    except Exception as e:
        print(e)
        print("\n\n!!Achtung!! Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung bereits veröffentlicht sein kann oder nicht!\n")