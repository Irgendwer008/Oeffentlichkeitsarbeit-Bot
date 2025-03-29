from datetime import datetime, timedelta
from inspect import stack, getmodule
import importlib.util
import sys
from os import listdir, getcwd, path, makedirs, environ, remove
from PyQt6.QtWidgets import QFileDialog, QApplication
from yaml import safe_load
from ttkbootstrap import Treeview

import my_dataclasses

YES = ["Y", "y", "Yes", "yes", "Ja", "ja"]
NO = ["N", "n", "No", "no", "Nein", "nein"]

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

## Be advised: The following parts for dynamic import of the credentials module where written by ChatGPT
def get_Logindaten():
    # Get paths
    base_path = path.dirname(sys.executable) if getattr(sys, 'frozen', False) else path.dirname(path.abspath(__file__))
    credentials_path = path.join(base_path, 'credentials.py')

    # Dynamically load credentials.py if it exists
    if path.exists(credentials_path):
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
## End of ChatGPT Codemain

def file_open_dialog(title: str, filetypes: str, directory: str = "") -> str:
    
        environ['QT_QPA_PLATFORM'] = 'xcb'
        qt_app = None

        if qt_app is None:
            qt_app = QApplication(sys.argv)
            
        file_name, _ = QFileDialog.getOpenFileName(None, title, directory, filetypes)
        
        return file_name

def get_list_of_eventfilepaths(relative_directory_path: str = "events/") -> list[str]:
    
    directory_path = getcwd() + "/" + relative_directory_path
    
    # Create directory if it doesn't exist yet
    makedirs(directory_path, exist_ok=True)
    
    full_path_list = []
    
    for event_path in listdir(directory_path):
        full_path_list.append(directory_path + event_path)
    
    return full_path_list

def get_event(filepath: str) -> my_dataclasses.Event:
    with open(filepath, "r") as file:
        yaml_data = safe_load(file)

        new_event = my_dataclasses.Event(
            DATEIPFAD=filepath,
            NAME=yaml_data["name"],
            BESCHREIBUNG=yaml_data["beschreibung"],
            BEGINN=datetime.fromisoformat(yaml_data["beginn"]),
            ENDE=datetime.fromisoformat(yaml_data["ende"]),
            BILD_DATEIPFAD=yaml_data["bild_dateipfad"],
            AUSGEWÄHLTE_KATEGORIE=yaml_data["ausgewählte_kategorie"],
            UNTERÜBERSCHRIFT=yaml_data["unterüberschrift"],
            LOCATION=yaml_data["veranstaltungsort"]["name"],
            STRASSE=yaml_data["veranstaltungsort"]["strasse"],
            PLZ=yaml_data["veranstaltungsort"]["plz"],
            STADT=yaml_data["veranstaltungsort"]["stadt"],
            LINK=yaml_data["veranstaltungsort"]["link"]
        )
        
        return new_event
    
def validate_min_max(input, widget, min, max):
    if len(input) >= min and len(input <= max):
        widget.configure(bootstyle = "success")
        return True
    else:
        widget.configure(bootstyle = "warning")
        return False

def get_selected_events(table: Treeview) -> list[my_dataclasses.Event]:
    results = []
    
    for focus_item in table.selection():
        table_item = table.item(focus_item)
        
        results.append(get_event(table_item["values"][2]))
    
    return results

def delete_file(filepath: str) -> None:
    if path.isfile(filepath):
        remove(filepath)
    return

Logindaten = get_Logindaten()