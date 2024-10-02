from dataclasses import dataclass
from datetime import datetime, timedelta
from inspect import stack, getmodule
import sys
import os
import importlib.util
import time

YES = ["Y", "y", "Yes", "yes", "Ja", "ja"]
NO = ["N", "n", "No", "no", "Nein", "nein"]

@dataclass
class Veranstaltungsdetails:
    NAME: str 
    BESCHREIBUNG: str
    BEGINN: datetime
    ENDE: datetime
    BILD_DATEIPFAD: str
    AUSGEWÄHLTE_KATEGORIE: list[str | None] # Number or None, if no category needed existant
    UNTERÜBERSCHRIFT: str = "Eine Z10-e.V. Veranstaltung"
    LOCATION: str = "Studentenzentrum Z10 e.V."
    STRASSE: str = "Zähringerstraße 10"
    PLZ: str = "76131"
    STADT: str = "Karlsruhe"
    LINK: str = "https://z10.info"

@dataclass
class PluginInfo:
    FRIENDLYNAME: str
    DEFAULTCATEGORY_KEY: str
    KATEGORIEN: dict[str: str]
                                                    
def round_nearest_30min(dtobj: datetime, earlier: bool = False) -> datetime:
    """Rounds time to nearest half hour

    Args:
        dtobj (datetime): Datetime to be rounded
        earlier (bool, optional): Whether the time should be rounded up (-> Later, False) or down (-> Earlier, True). Defaults to False.

    Returns:
        datetime: resulting datetime
    """
    
    result = dtobj.replace(minute=30 - 30 * earlier)
    result += timedelta(minutes=dtobj.minute - dtobj.minute % 30)
    return result

def step(text: str):
    print(format.ORANGE + getmodule(stack()[1][0]).plugininfo.FRIENDLYNAME + ": " + text + "                                                             " + format.CLEAR, end="\n\n")

def reset_screen(heading: str = None):
    print(chr(27) + "[H" + chr(27) + "[J", end="")
    
    print(format.BOLD, end="")
    
    print("######################")
    print("#                    #")
    print("#  Z10 Autouploader  #")
    print("#                    #")
    print("######################")
    
    print(format.CLEAR, end="")
    
    print(format.info("Drücke jederzeit <Ctrl> + <C>, um das Programm zu beenden."))
    
    if heading is not None:
        # Print heading
        print(format.bold(heading))
        
        # Print heading underline
        print("\u2558", end="")
        for i in range(0, len(heading) + 2):
            print("\u2550", end="")
        print("\u255B")
    else:
        print("")

    
class format:
    CLEAR = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[38;5;14m"
    INFO = CYAN
    RED = "\033[38;5;9m"
    WARNING = RED
    ORANGE = "\033[38;2;255;140;15m"
    GREEN = "\033[38;5;10m"
    INFO_ICON = "\U0001F6C8"
    WARNING_ICON = "\u26A0" 
    
    def bold(text: str) -> str:
        return format.BOLD + "\n  " + text + format.CLEAR

    def info(text: str) -> str:
        return format.INFO + "\n" + format.INFO_ICON + " " + text + format.CLEAR

    def error(text: str) -> str:
        #reset_screen()
        return format.WARNING + "\n" + format.WARNING_ICON + " " + text + format.CLEAR
    
    def overview_print(text: str):
        print("\u2502 {:<28}\u2551  ".format(text + (":" if text != "" else " ")), end="")
        
    def overview_newline():
        print("\u251C", end="")
        for i in range(1, 30):
            print("\u2500", end="")
        print("\u256B", end="")
        for i in range(1, 60):
            print("\u2500", end="")
        print("")
        
    def quote(text: str) -> str:
        return "\"" + text + "\""


## Be advised: The following parts for dynamic import of the credentials module where written by ChatGPT
def get_Logindaten():
    # Get paths
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_path, 'credentials.py')

    # Dynamically load credentials.py if it exists
    if os.path.exists(credentials_path):
        spec = importlib.util.spec_from_file_location('credentials', credentials_path)
        credentials = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(credentials)
            
        # Access the Logindaten class from credentials.py
        if hasattr(credentials, 'Logindaten'):
            # Now you can use the variables/functions from credentials.py
            print(f"Loaded credentials")
            return credentials.Logindaten  # Return reference to the Logindaten class
        else:
            raise ImportError("Logindaten class not found in credentials.py")
    else:
        print(format.error("Fehler: credentials.py konnte nicht gefunden werden. Ist eine gültige credentials.py-Datei im selben Verzeichnis wie dieses Programm?"))
        input("\n> ")
        sys.exit(1)
        
Logindaten = get_Logindaten()
## End of ChatGPT Code