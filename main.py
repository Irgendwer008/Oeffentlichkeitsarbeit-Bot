#!/usr/bin/env python

from datetime import datetime
from os.path import exists
from os.path import abspath
import time
from pwinput import pwinput
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from credentials import _Logindaten
from helper import Veranstaltungsdetails, format, reset_screen, round_nearest_30min, YES, NO
    
import KalenderKarlsruhe
import Nebenande
import StuWe
import Z10Website
import Venyoo
plugins = [KalenderKarlsruhe, Nebenande, StuWe, Z10Website, Venyoo]

from os.path import abspath
    
#TODO: Check if events where published correctly (prob takes much time :,) )
#TODO: try facebok-sdk (see link at top of Meta.py)
#TODO: Get actual available categories from websites
#TODO: Add a lot of comments for better readability :D
#TODO: Add summary for double checking before starting uploading
#TODO: Change significant comments to step() in all plugins
#TODO: StuWe Dates not working

def get_plugins() -> list:
    while True:
        # print all available plugins with number
        print("\n# Auf welchen Platformen soll die Veranstaltung veröffentlicht werden? Gib \"Alle\" wenn alle Plugins, oder die entsprechende(n) Zahl(en), mit Komma getrennt, an:\n")
        for i in range(1, len(plugins) + 1):
            print(" [" + str(i) + "] " + plugins[i-1].plugininfo.FRIENDLYNAME)
            
        # recieve answer
        answer = input("\n> ")
        
        print("\n'" + answer + "'\n")
        
        if answer == "^[[A":
            print("Yay")
        exit()
        
        # check, if "Alle" was selected
        if answer.lower() in ["alle", "allen", "all"]:
            return plugins
        
        # if not, split the answer-string at every comma
        choices = answer.split(",")
            
        # Catch invalid input
        try:
            if len(choices) < 1:            # Catch no input
                raise Exception
            
            choices = set(choices)          # remove duplicate numbers and sort
                
            new_plugins_list = []
            
            for choice in choices:          # Iterate over every given choice
                number = int(choice) - 1    # Catch choice not a integer
                if number not in range(0, len(plugins)):    # Catch number out of range
                    raise Exception
                new_plugins_list.append(plugins[number])
            
            return new_plugins_list
                
                
        except:
            pass
        print(format.error("Deine Eingabe war fehlerhaft. Bitte versuche es erneut."))
            
def print_current_plugins():
    print(format.info("Es werden folgende Plugins verwendet werden: \n"))
    for plugin in plugins:
        print(format.INFO + "  " + plugin.plugininfo.FRIENDLYNAME + format.CLEAR)
    input("\n Zum Vortsetzen, drücke eine beliebige Taste.\n> ")
    
def get_Z10_credetials() -> tuple[str, str]:
    try:
        if Z10Website in plugins:
            pass
    except:
            return ("", "")
    
    username = ""
    password = ""
    
    while username == "":
        username = input("\n# Wie lautet dein Z10-Benutzername (Kürzel)?: \n> ")
    while password == "":
        password = pwinput("\n# Wie lautet dein Z10-Passwort?: \n> ", "*")
        
    return (username, password)    

def get_name() -> str:
    name = ""
    while name == "":
        name = input("\n# Wie lautet der Titel der Veranstaltung?: \n> ")
        
        # check length limitations
        if len(name) not in range (2, 60):
            print(format.error("Titel muss zwischen einschließlich zwei und 60 Zeichen lang sein!"))
            name = ""
    return name
        
def get_unterüberschrift() -> str:
    unterüberschrift = input("\n# Wie lautet die Unterüberschrift der Veranstaltung? (Optional, Standard ist '" + Veranstaltungsdetails.UNTERÜBERSCHRIFT + "'): \n> ")
    if unterüberschrift == "":
        unterüberschrift = Veranstaltungsdetails.UNTERÜBERSCHRIFT
    return unterüberschrift
        
def get_beschreibung() -> str:
    beschreibung = ""
    while beschreibung == "":
        beschreibung = input("\n# Wie lautet die Beschreibung der Veranstaltung?: \n> ")
        
        # check length limitations
        if len(beschreibung) not in range (2, 5000):
            print(format.error("Beschreibung muss zwischen einschließlich zwei und 60 Zeichen lang sein!"))
            beschreibung = ""
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
            print(format.error("Deine Eingabe hat das falsche Format oder liegt in der Vergangenheit! Bitte gib Datum und Uhrzeit anhand des Beispiels an."))
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
            print(format.error("Deine Eingabe \"" + string + "\" hat das falsche Format oder liegt vor dem Beginn der Veranstaltung! Bitte gib Datum und Uhrzeit anhand des Beispiels an oder lasse dieses Feld frei, wenn du keine Endzeit angeben möchtest."))
    return veranstaltungsende

def get_location() -> list[str, str, str, str]:
    while True:
        answer = input("\n# Ist die Location / Venue \"" + Veranstaltungsdetails.LOCATION + "\" und die Addresse \"" + Veranstaltungsdetails.STRASSE + ", " + Veranstaltungsdetails.PLZ + " " + Veranstaltungsdetails.STADT + "\" zutreffend?: [Y/n]\n> ")
        
        # if default should be kept, break
        yes = YES
        yes.append("")
        if answer in yes:
            return Veranstaltungsdetails.LOCATION, Veranstaltungsdetails.STRASSE, Veranstaltungsdetails.PLZ, Veranstaltungsdetails.STADT
        
        # elif not, ask for new values. Else retry for valid input
        elif answer in NO:
            
            # Location
            location = ""
            while location == "":
                location = input("\n# Wie lautet die Location / Venue der Veranstaltung? (Optional, Standard ist '" + Veranstaltungsdetails.LOCATION + "'): \n> ")
            
            # Straße
            strasse = ""
            while strasse == "":
                strasse = input("\n# Wie lautet die Straße der Addresse? (Optional, Standard ist '" + Veranstaltungsdetails.STRASSE + "'): \n> ")
            
            # Location
            plz = ""
            while plz == "":
                try:
                    plz = str(int(input("\n# Wie lautet die PLZ der Addresse? (Optional, Standard ist '" + Veranstaltungsdetails.PLZ + "'): \n> ")))
                except:
                    print(format.error("Bitte nenne eine valide PLZ!"))
            
            # Location
            stadt = ""
            while stadt == "":
                stadt = input("\n# Wie lautet die Stadt der Addresse? (Optional, Standard ist '" + Veranstaltungsdetails.STADT + "'): \n> ")
            
            return location, strasse, plz, stadt

def notify_of_rounded_times(beginn: datetime, ende: datetime):
    if beginn.minute % 30 != 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebene Anfangsuhrzeit wird auf " + round_nearest_30min(beginn).strftime("%H:%M"), end=" gerundet"))
    elif ende is not None and ende.minute % 30 != 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebene Enduhrzeit wird auf " + round_nearest_30min(ende, True).strftime("%H:%M"), end=" gerundet"))
    elif beginn.minute % 30 != 0 and ende is not None and ende.minute % 30 != 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebenen Uhrzeiten werden auf " + round_nearest_30min(beginn, True).strftime("%H:%M") + " bzw. " + round_nearest_30min(ende, True).strftime("%H:%M"), end=" gerundet"))

    print("")
    
    time.sleep(1)
    
    return
    
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
        askstring = "\nSollen die Standardkategorien\n\n"            
        for plugin in plugins:
            # add line, if this plugin uses categories
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                askstring += "  " + plugin.plugininfo.FRIENDLYNAME + ": \"" + plugin.plugininfo.KATEGORIEN[plugin.plugininfo.DEFAULTCATEGORY_KEY] + "\",\n"
        askstring += "\nbeibehalten werden? [Y/n]\n> "
        
        # ask if default categories should be kept
        default_categories = input(askstring)
        
        # if so, break
        yes = YES
        yes.append("")
        if default_categories in yes:
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

def get_bild() -> str:
    filepath = input("\n# Wie lautet der Dateipfad zum Bild der Veranstaltung?: \n> ")
        
    while not exists(filepath) or not (filepath.endswith(".png") or filepath.endswith(".jpg") or filepath.endswith(".gif")):
        filepath = input(format.error("Bitte nenne einen existierenden dateipfad: "))
    return abspath(filepath)

def get_link() -> str:
    link = input("\n# Wie lautet der Link ? (Optional, Standard ist '" + Veranstaltungsdetails.LINK + "'): \n> ")
    if link == "":
        link = Veranstaltungsdetails.LINK
    return link

if __name__ == "__main__":
    
    # Get event details
    try:        
    
        reset_screen(heading="Plugins")
        plugins = get_plugins()
        print_current_plugins()
        
        reset_screen(heading="Z10 Benutzerkonto")
        username, password = get_Z10_credetials()
        
        reset_screen(heading="Titel und Beschreibung")
        name = get_name()
        unterüberschrift = get_unterüberschrift()
        beschreibung=get_beschreibung()
        
        reset_screen(heading="Zeiten")
        beginn = get_beginn()
        ende = get_ende(beginn)
        notify_of_rounded_times(beginn, ende)
        
        reset_screen(heading="Veranstaltungsort")
        location, strasse, plz, stadt = get_location()
        
        reset_screen(heading="Kategorien")
        kategorien = get_kategorien()
        
        reset_screen(heading="Bild und Link")
        bild = get_bild()
        link = get_link()
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet. Die Veranstaltung wurde nicht veröffentlicht.\n")
        exit()
        
        
    details = Veranstaltungsdetails(NAME = name, 
                                    UNTERÜBERSCHRIFT = unterüberschrift,
                                    BESCHREIBUNG = beschreibung,
                                    BEGINN = beginn,
                                    ENDE = ende,
                                    LOCATION = location,
                                    STRASSE = strasse,
                                    PLZ = plz,
                                    STADT = stadt,
                                    BILD_DATEIPFAD = abspath(bild),
                                    LINK = link,
                                    AUSGEWÄHLTE_KATEGORIE = kategorien)
    
    # Values may be *temporarily* hardcorded here for faster Testing of plugins so that one doesn't have to type every detail every time. Comment for normal functionality
    """
    details = Veranstaltungsdetails(NAME = "Test",
                                    UNTERÜBERSCHRIFT = "Dies ist eine Testbeschreibung",
                                    BESCHREIBUNG = "Dies ist eine Beispielbeschreibung",
                                    BEGINN = datetime.strptime("31.10.2024 20:00", "%d.%m.%Y %H:%M"),
                                    ENDE = datetime.strptime("31.10.2024 23:50", "%d.%m.%Y %H:%M"),
                                    BILD_DATEIPFAD = abspath("image.jpg"),
                                    AUSGEWÄHLTE_KATEGORIE = kategorien)
    """
    
    # Get login credentials
    credentials = _Logindaten(Z10_USERNAME = username,
                              Z10_PASSWORD = password)
    
    # init driver    
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.set_preference("permissions.default.desktop-notification", 2)
    #options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    
    # Newline
    print("")
    
    # Execute all the plugins
    try:
        lastsuccesful = 0
        for plugin in plugins:
            try:
                plugin.run(details, credentials, plugins, driver)
                print("Veranstaltung erfolgreich auf " + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + " veröffentlicht.")
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print("\n\n" + e.with_traceback + "\n\n")
                print("\n\n!!Achtung\u26A0 Es gab einen Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n")
            lastsuccesful += 1
        driver.quit()
    except KeyboardInterrupt:
        print("\n\n!!Achtung\u26A0 Das Programm wurde vom Benutzer während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung bereits veröffentlicht sein kann oder nicht!\n")
        driver.quit()
    except Exception as e:
        print("\n\n!!Achtung\u26A0 Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung veröffentlicht sein kann oder auch nicht!\n")
        driver.quit()
        raise e
    
    driver.quit()