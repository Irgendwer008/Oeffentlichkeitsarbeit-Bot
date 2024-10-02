#!/usr/bin/env python

import argparse
from datetime import datetime
from os.path import exists, abspath
from os import system
from pwinput import pwinput
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sys import exit

system("")

# Allow command line argument handling before anything else
parser = argparse.ArgumentParser(
    description = "Automatisiertes Veröffentlichen von Events auf einer Reihe von Platformen",
    epilog = "Mehr auf Github: https://github.com/Irgendwer008/Oeffentlichkeitsarbeit-Bot")

parser.add_argument(
    "-w", 
    "--not-headless", 
    dest="headless", 
    default=True, 
    action="store_false", 
    help="Ist diese Flagge gesetzt öffnet sich Firefox als Fenster. Wenn nicht, läuft es nur im Hintergrund")

parser.set_defaults(flag=True)
args = parser.parse_args()

# Auxiliary imports
from helper import Veranstaltungsdetails, format, reset_screen, round_nearest_30min, YES, NO
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Import Logindaten only for type hinting (not at runtime)
    from credentials import Logindaten
else:
    from helper import Logindaten
    
# Plugin imports
import Plugins.KalenderKarlsruhe as KalenderKarlsruhe
import Plugins.Nebenande as Nebenande
import Plugins.StuWe as StuWe
import Plugins.Z10Website as Z10Website
import Plugins.Venyoo as Venyoo
available_plugins = [KalenderKarlsruhe, Nebenande, StuWe, Z10Website, Venyoo]



#TODO: Check if events where published correctly (prob takes much time :,) )
#TODO: try facebok-sdk (see link at top of Meta.py)
#TODO: Get actual available categories from websites
#TODO: Add a lot of comments for better readability :D
#TODO: Add docstrings for better readability :D
#TODO: Venyoo working custom category
#TODO: Way to go back one step and change previous input
#TODO: Wrap Zeilen von langem Text in Beschreibung in Overview
#TODO: add credentials import from seperate file
#TODO: add argument implementation for credentials and image file
#TODO: Update website locales in README.md


def get_plugins() -> list:
    while True:
        # print all available plugins with number
        print("\n# Auf welchen Platformen soll die Veranstaltung veröffentlicht werden? Gib \"Alle\" wenn alle Plugins, oder die entsprechende(n) Zahl(en), mit Komma getrennt, an:\n")
        for i in range(1, len(available_plugins) + 1):
            print(" [" + str(i) + "] " + available_plugins[i-1].plugininfo.FRIENDLYNAME)
            
        # recieve answer
        answer = input("\n> ")
        
        # check, if "Alle" was selected
        if answer.lower() in ["alle", "allen", "all"]:
            return available_plugins
        
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
                if number not in range(0, len(available_plugins)):    # Catch number out of range
                    raise Exception
                new_plugins_list.append(available_plugins[number])
            
            return new_plugins_list
                
                
        except:
            pass
        print(format.error("Deine Eingabe war fehlerhaft. Bitte versuche es erneut."))
            
def print_current_plugins(plugins: list):
    print(format.info("Es werden folgende Plugins verwendet werden: \n"))
    for plugin in plugins:
        print(format.INFO + "  " + plugin.plugininfo.FRIENDLYNAME + format.CLEAR)
    input("\n Zum Vortsetzen, drücke <Enter>.\n> ")
    
def get_Z10_credetials(ls: list) -> tuple[str, str]:
    username = ""
    password = ""
    
    while username == "":
        username = input("\n# Wie lautet dein Z10-Benutzername (Kürzel)?: \n> ")
        format.error("Bitte nenne dein Kürzel: ")
    while password == "":
        password = pwinput("\n# Wie lautet dein Z10-Passwort?: \n> ", "*")
        format.error("Bitte nenne dein Passwort: ")
        
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

def get_ende(veranstaltungsbeginn: datetime) -> datetime:
    veranstaltungsende = None
    while (True):
        
        string = input("\n# Wann endet die Veranstaltung? (Format: 01.02.2024 17:42): \n> ")
        
        try:
            veranstaltungsende = datetime.strptime(string, "%d.%m.%Y %H:%M")
            if veranstaltungsende < veranstaltungsbeginn:
                raise Exception
            break
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print(format.error("Deine Eingabe \"" + string + "\" hat das falsche Format oder liegt vor dem Beginn der Veranstaltung (" + veranstaltungsbeginn.strftime("%d.%m.%Y %H:%M") + ")! Bitte gib Datum und Uhrzeit anhand des Beispiels an oder lasse dieses Feld frei, wenn du keine Endzeit angeben möchtest."))
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
    if beginn.minute % 30 != 0 and ende.minute % 30 == 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebene Anfangsuhrzeit wird auf " + round_nearest_30min(beginn).strftime("%H:%M") + " gerundet"))
    elif beginn.minute % 30 == 0 and ende.minute % 30 != 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebene Enduhrzeit wird auf " + round_nearest_30min(ende, True).strftime("%H:%M") + " gerundet"))
    elif beginn.minute % 30 != 0 and ende.minute % 30 != 0:
        print(format.info("Hinweis: Nebenan.de akzeptiert nur Uhrzeiten zur halben und vollen Stunde. Die angegebenen Uhrzeiten werden auf " + round_nearest_30min(beginn).strftime("%H:%M") + " bzw. " + round_nearest_30min(ende, True).strftime("%H:%M") + " gerundet"))

    if beginn.minute % 30 != 0 or ende.minute % 30 != 0:
        input("\n Zum Vortsetzen, drücke <Enter>.\n> ")
    return
    
def get_kategorien(plugins: list) -> list[str]:
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
        max_length = 0
        for plugin in plugins:
            # add line, if this plugin uses categories
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                max_length = max(max_length, len(plugin.plugininfo.FRIENDLYNAME))
                
        # dynamically generate question
        askstring = "\nSollen die Standardkategorien\n\n"            
        for plugin in plugins:
            # add line, if this plugin uses categories
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                askstring += ("{:<%i}" %(max_length + 5)).format("  " + plugin.plugininfo.FRIENDLYNAME + ":") + " \"" + plugin.plugininfo.KATEGORIEN[plugin.plugininfo.DEFAULTCATEGORY_KEY] + "\",\n"
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
                    available_categories = list(plugin.plugininfo.KATEGORIEN.keys())
                    while True:
                        print("\nWelche Kategorie soll für \"" + plugin.plugininfo.FRIENDLYNAME + "\" verwendet werden? Bitte gib die entsprechende Zahl (1-" + str(len(plugin.plugininfo.KATEGORIEN)) + ") an:\n")
                        for i in range(1, len(available_categories) + 1):
                            print(" {:<5} ".format(f"[{str(i)}]") + plugin.plugininfo.KATEGORIEN[available_categories[i-1]])
                        try:
                            # try assigning this key to the list
                            ausgewählte_kategorien.append(available_categories[int(input("\n> "))-1])
                            print("" + format.info("\"" + plugin.plugininfo.FRIENDLYNAME + "\" wird die Kategorie \"" + plugin.plugininfo.KATEGORIEN[ausgewählte_kategorien[-1]] + "\" verwenden."))
                            break
                        except KeyboardInterrupt as e:
                            raise e
                        except Exception as e:
                            # here for debuggin purposes
                            raise e
                            print("\nDies ist keine valide Option!\n")
                            
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

def print_summary(plugins: list, details: Veranstaltungsdetails, credentials: Logindaten):
    print(format.info("Hier kannst du die eingegebenen Daten überprüfen. Schaue noch einmal gut drüber, denn nach dem Veröffentlichen müssen Änderungen manuell auf jeder Platform einzeln angewendet werden: \n"))
    
    ## Plugins
    format.overview_print("Platformen")
    # Print first plugin inline with tile
    print("- " + plugins[0].plugininfo.FRIENDLYNAME)
    # Print rest of plugins
    if len(plugins) > 1:
        for plugin in plugins[1:]:
            format.overview_print("")
            print("- " + plugin.plugininfo.FRIENDLYNAME)
            
    format.overview_newline()
    
    # Z10 Credentials
    if (username, password) != ("", ""):
        format.overview_print("Z10 Benutzername")
        print(credentials.Z10_USERNAME)
    
        format.overview_newline()
    
    # Name
    format.overview_print("Titel")
    print(details.NAME)
    
    format.overview_newline()
    
    # Unterüberschrift
    format.overview_print("Unterüberschrift")
    print(details.UNTERÜBERSCHRIFT)
    
    format.overview_newline()
    
    # Beschreibung
    format.overview_print("Beschreibung")
    print(details.BESCHREIBUNG)
    
    format.overview_newline()
    
    # Zeiten
    format.overview_print("Startdatum und -zeit")
    print(details.BEGINN.strftime("%d.%m.%Y %H:%M"))
    format.overview_print("Enddatum und -zeit")
    print(details.ENDE.strftime("%d.%m.%Y %H:%M"))
    
    format.overview_newline()
    
    # Location
    format.overview_print("Location / Venue")
    print(details.LOCATION)
    format.overview_print("Addresse")
    print(details.STRASSE + ", " + details.PLZ + " " +details.STADT)
    
    format.overview_newline()
    
    # Kategorien
    # Check if there are any plugins that use categories
    
    if kategorien != []:
        format.overview_print("Kategorien")
        
        max_length = 0
        for plugin in plugins:
            # add line, if this plugin uses categories
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                max_length = max(max_length, len(plugin.plugininfo.FRIENDLYNAME))
                
        first = True
        for plugin in plugins:
            if plugin.plugininfo.DEFAULTCATEGORY_KEY is not None:
                if first:
                    first = False
                else:
                    format.overview_print("")
                print(format.BOLD + ("{:<%i}" %(max_length + 5)).format(plugin.plugininfo.FRIENDLYNAME + ":") + " \"" + plugin.plugininfo.KATEGORIEN[details.AUSGEWÄHLTE_KATEGORIE[plugins.index(plugin)]] + "\"")
            
        format.overview_newline()
    
    # Bild und Link
    format.overview_print("Bild-Dateipfad")
    print(format.quote(details.BILD_DATEIPFAD))
    format.overview_print("Link")
    print(format.quote(details.LINK))

            
    ## Confirm all
    while True:
        confirm = input(f"\n{format.ORANGE}Zum Bestätigen, drücke <Enter>. Tippe \"Abbrechen\", um den Vorgang abzubrechen\n> " + format.CLEAR)
        if confirm == "":
            return
        if confirm.lower() == "abbrechen":
            exit(1)

if __name__ == "__main__":
    
    # Get event details
    try:        
        # Plugins
        reset_screen(heading="Plugins")
        plugins = get_plugins()
        print_current_plugins(plugins)
        
        # Z10 user account
        if Z10Website in plugins:
            reset_screen(heading="Z10 Benutzerkonto")
            username, password = get_Z10_credetials(plugins)
        else:
            username, password = ("", "")
        
        # Title and description
        reset_screen(heading="Titel und Beschreibung")
        name = get_name()
        unterüberschrift = get_unterüberschrift()
        beschreibung=get_beschreibung()
        
        # Dates and times
        reset_screen(heading="Zeiten")
        beginn = get_beginn()
        ende = get_ende(beginn)
        if Nebenande in plugins:
            notify_of_rounded_times(beginn, ende)
        
        # Location
        reset_screen(heading="Veranstaltungsort")
        location, strasse, plz, stadt = get_location()
        
        # Categories
        reset_screen(heading="Kategorien")
        kategorien = get_kategorien(plugins)
        
        # Image and link path / uri
        reset_screen(heading="Bild und Link")
        bild = abspath(get_bild())
        link = get_link()
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet. Die Veranstaltung wurde nicht veröffentlicht.\n")
        exit(1)
        
    # Enter event details
    details = Veranstaltungsdetails(NAME = name, 
                                    UNTERÜBERSCHRIFT = unterüberschrift,
                                    BESCHREIBUNG = beschreibung,
                                    BEGINN = beginn,
                                    ENDE = ende,
                                    LOCATION = location,
                                    STRASSE = strasse,
                                    PLZ = plz,
                                    STADT = stadt,
                                    BILD_DATEIPFAD = bild,
                                    LINK = link,
                                    AUSGEWÄHLTE_KATEGORIE = kategorien)
    
    # Enter necessary login credentials
    credentials = Logindaten(Z10_USERNAME = username,
                              Z10_PASSWORD = password)
    
    # Print summary
    reset_screen("Übersicht")
    print_summary(plugins, details, credentials)
        
    # init driver    
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.set_preference("permissions.default.desktop-notification", 2)
    if args.headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    
    # Newline
    print("")
    
    # Execute all the plugins
    try:
        lastsuccesful = 0
        for plugin in plugins:
            try:
                plugin.run(details, credentials, plugins, driver)
                print(format.GREEN +  "Veranstaltung erfolgreich auf " + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + " veröffentlicht." + format.CLEAR)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print("\n\n" + str(e.with_traceback) + "\n\n")
                print(format.error("Achtung \u26A0 Es gab einen Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
            lastsuccesful += 1
        driver.quit()
    except KeyboardInterrupt:
        print(format.error("Achtung \u26A0 Das Programm wurde vom Benutzer während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
        driver.quit()
    except Exception as e:
        print(e)
        print(format.error("Achtung \u26A0 Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung veröffentlicht sein kann oder auch nicht!\n"))
        driver.quit()
        raise e
    
    driver.quit()