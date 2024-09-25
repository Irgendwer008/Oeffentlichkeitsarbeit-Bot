from datetime import datetime
from os.path import exists
from os.path import abspath
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from credentials import _Logindaten
from helper import Veranstaltungsdetails, round_nearest_30min, YES, NO
    
import KalenderKarlsruhe
import Nebenande
import Meta
plugins = [Meta]

from os.path import abspath
    
#TODO: check for valid values: locale (datepicker nebenan.de)
#TODO: Make categories functional
#TODO: Allow choosing of which plugins to use
#TODO: Check if events where published correctly (prob takes much time :,) )
#TODO: limit text lengths: Nebenande: titel: 2 <= text <= 60, Beschreibung: 2 <= text <= 5000
#TODO: add adding of default category to helper.Veranstaltungsdetails.AUSGEWÄHLTE_KATEGORIE

def get_name() -> str:
    name = ""
    while name == "":
        name = input("\n# Wie lautet der Titel der Veranstaltung?: \n> ")
    return name
        
def get_unterüberschrift() -> str:
    unterüberschrift = input("\n# Wie lautet die Unterüberschrift der Veranstaltung? (Optional, Standart ist '" + Veranstaltungsdetails.UNTERÜBERSCHRIFT + "'): \n> ")
    if unterüberschrift == "":
        unterüberschrift = Veranstaltungsdetails.UNTERÜBERSCHRIFT
    return unterüberschrift
        
def get_beschreibung() -> str:
    beschreibung = ""
    while beschreibung == "":
        beschreibung = input("\n# Wie lautet die Beschreibung der Veranstaltung?: \n> ")
    return beschreibung

def get_beginn() -> datetime:
    while (True):
        try:
            veranstaltungsbeginn = datetime.strptime(input("\n# Wann beginnt die Veranstaltung? (Format: 01.02.2024 17:42): \n> "), "%d.%m.%Y %H:%M")
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
        
        string = input("\n# Wann endet die Veranstaltung? Lasse dieses Feld frei, wenn deine Veranstaltung keine bestimmte Endzeit hat. (Format: 01.02.2024 17:42): \n> ")
                    
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
    filepath = input("\n# Wie lautet der Dateipfad zum Bild der Veranstaltung?: \n> ")
        
    while not exists(filepath) or not (filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".gif")):
        filepath = input("\n!! Bitte nenne einen existierenden dateipfad: ")
    return abspath(filepath)
    
def get_kategorien() -> list[str]:
    default_categories = ""
    ausgewählte_kategorien = []
    
    # Check if there are any plugins that use categories
    any_categories_needed = False
    for plugin in plugins:
        if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
            any_categories_needed = True
            break
    if not any_categories_needed:
        return []
    
    while True:
        # dynamically generate question
        askstring = "\nSollen die Standartkategorien\n\n"            
        for plugin in plugins:
            # add line, if this plugin uses categories
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                askstring += "  " + plugin.plugininfo.FRIENDLYNAME + ": \"" + plugin.plugininfo.KATEGORIEN[plugin.plugininfo.DEFAULTCATEGORY_KEY] + "\",\n"
        askstring += "\nbeibehalten werden? [Y/n]\n> "
        
        # ask if default categories should be kept
        default_categories = input(askstring)
        
        # if so, break
        if default_categories in [YES, ""]:
            for plugin in plugins:
                ausgewählte_kategorien.append(plugin.plugininfo.DEFAULTCATEGORY_KEY)
            break
        
        # if not, ask for new categories
        elif default_categories in NO:            
            for plugin in plugins:
                # if this plugin doesnt use categories, set this list entry to None
                if plugin.plugininfo.DEFAULTCATEGORY_KEY is None:
                    ausgewählte_kategorien.append(None)
                # if it does use categories, ask which one should be used and assign it's key to the list
                else:
                    while True:
                        print("\nWelche Kategorie soll für \"" + plugin.plugininfo.FRIENDLYNAME + "\" verwendet werden? Bitte gib die entsprechende Zahl (1-" + str(len(plugin.plugininfo.KATEGORIEN)) + ") an: ")
                        for i in range(1, len(plugin.plugininfo.KATEGORIEN) + 1):
                            print(" [" + str(i) + "] " + plugin.plugininfo.KATEGORIEN[list(plugin.plugininfo.KATEGORIEN)[i-1]])
                        try:
                            # try assigning this key to the list
                            ausgewählte_kategorien.append(list(plugin.plugininfo.KATEGORIEN)[int(input("> "))-1])
                            print("\n\"" + plugin.plugininfo.FRIENDLYNAME + "\" wird die Kategorie \"" + plugin.plugininfo.KATEGORIEN[list(plugin.plugininfo.KATEGORIEN)[i-1]] + "\" verwenden.")
                            break
                        except KeyboardInterrupt as e:
                            raise e
                        except Exception as e:
                            print("\nThat is not a valid option!\n")
                            
            # little easter egg, if you will
            those_are_the_default_values_tho = True
            for i in range(0, len(plugins)):
                if plugins[i].plugininfo.DEFAULTCATEGORY_KEY != ausgewählte_kategorien[i]:
                    those_are_the_default_values_tho = False
            if those_are_the_default_values_tho:
                print("\nAber... das... das sind doch schon die Standardwerte? Wie auch immer, weiter gehts:\n")
                
            break
        
    
    return ausgewählte_kategorien

if __name__ == "__main__":
    
    print("######################")
    print("#                    #")
    print("#  Z10 Autouploader  #")
    print("#                    #")
    print("######################")
    
    # Get event details
    try:
        # Values may be hardcorded here for faster Testing of plugins so that one doesn't have to type every detail every time
        details = Veranstaltungsdetails(NAME = "Test", #get_name(), 
                                        UNTERÜBERSCHRIFT = "Dies ist eine Testbeschreibung", #get_unterüberschrift(),
                                        BESCHREIBUNG = "Dies ist eine Beispielbeschreibung", #get_beschreibung(),
                                        BEGINN = datetime.strptime("31.10.2024 20:00", "%d.%m.%Y %H:%M"), #get_beginn(),
                                        ENDE = datetime.strptime("31.10.2024 23:50", "%d.%m.%Y %H:%M"), #get_ende(veranstaltungsbeginn),
                                        BILD_DATEIPFAD = abspath("image.jpg"), # get_bild())  
                                        AUSGEWÄHLTE_KATEGORIE = get_kategorien())
        notify_of_rounded_times(details.BEGINN, details.ENDE)   
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet. Die Veranstaltung wurde nicht veröffentlicht.\n")
        exit()
    
    # Get login credentials
    credentials = _Logindaten
    
    # init driver
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.set_preference("permissions.default.desktop-notification", 2)
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
        #driver.quit()
    except KeyboardInterrupt:
        print("\n\n!!Achtung!! Das Programm wurde vom Benutzer während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung bereits veröffentlicht sein kann oder nicht!\n")
    except Exception as e:
        print("\n\n!!Achtung!! Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung veröffentlicht sein kann oder auch nicht!\n")
        raise e