from dataclasses import dataclass
from datetime import datetime, timedelta
from inspect import stack, getmodule
import shutil
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
    print(getmodule(stack()[1][0]).plugininfo.FRIENDLYNAME + ": " + text + "                                                             ", end="\r")

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
    INFO = "\033[38;5;14m"
    WARNING = "\033[38;5;9m"
    INFO_ICON = "\U0001F6C8"
    WARNING_ICON = "\u26A0" 
    
    def bold(text: str) -> str:
        return format.BOLD + "\n  " + text + format.CLEAR

    def info(text: str) -> str:
        return format.INFO + "\n" + format.INFO_ICON + " " + text + format.CLEAR

    def error(text: str) -> str:
        reset_screen()
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