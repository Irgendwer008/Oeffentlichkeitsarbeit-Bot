from datetime import datetime, timedelta
from inspect import stack, getmodule
import importlib.util
import sys
#from os import listdir, getcwd, path, makedirs, environ, remove
from os import environ, remove
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QApplication
from yaml import safe_load
from ttkbootstrap import Treeview

from my_dataclasses import Event, Config

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
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
        
    credentials_path = base_path / Path("credentials.py")

    # Dynamically load credentials.py if it exists
    if Path.exists(credentials_path):
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

def get_list_of_eventfilepaths(events_directory_path: Path = Path("events")) -> list[Path]:
    
    directory_path = Path.cwd() / events_directory_path
    
    # Create directory if it doesn't exist yet
    if not events_directory_path.exists():
        events_directory_path.mkdir()
    
    path_list = []
    
    for event_path in directory_path.iterdir():
        path_list.append(event_path)
    
    return path_list

def get_event_from_path(filepath: Path) -> Event:
    with open(filepath.resolve(), "r") as file:
        yaml_data = safe_load(file)

        new_event = Event(
            DATEIPFAD=filepath,
            NAME=yaml_data["name"],
            BESCHREIBUNG=yaml_data["beschreibung"],
            BEGINN=datetime.fromisoformat(yaml_data["beginn"]),
            ENDE=datetime.fromisoformat(yaml_data["ende"]),
            BILD_DATEIPFAD=Path(yaml_data["bild_dateipfad"]).resolve(),
            AUSGEWÄHLTE_KATEGORIE=yaml_data["ausgewaehlte_kategorie"],
            UNTERÜBERSCHRIFT=yaml_data["unterueberschrift"],
            LOCATION=yaml_data["veranstaltungsort"]["name"],
            STRASSE=yaml_data["veranstaltungsort"]["strasse"],
            PLZ=yaml_data["veranstaltungsort"]["plz"],
            STADT=yaml_data["veranstaltungsort"]["stadt"],
            LINK=yaml_data["link"]
        )
        
        return new_event

def event_to_string(event: Event) -> str:
    return safe_load(f"""
name: '{event.NAME.replace("'", "\"")}'
beschreibung: '{event.BESCHREIBUNG.replace("'", "\"")}'
beginn: '{event.BEGINN.isoformat()}'
ende: '{event.ENDE.isoformat()}'
bild_dateipfad: '{event.BILD_DATEIPFAD}'
ausgewaehlte_kategorie: null
unterueberschrift: '{event.UNTERÜBERSCHRIFT}'
veranstaltungsort: 
  name: '{event.LOCATION}'
  strasse: '{event.STRASSE}'
  plz: '{event.PLZ}'
  stadt: '{event.STADT}'
link: '{event.LINK}'
        """)

def pathify_event(event: Event, duplicatenumber: int = 0) -> Path:
    
    words = [event.BEGINN.strftime("%Y-%m-%d")]
    
    for word in event.NAME.split():
        words.append(word.capitalize())
    
    if duplicatenumber > 0:
        words.append(str(duplicatenumber))
        
    filename = "_".join(words)
    
    return (Config.events_dir / Path(filename)).resolve()
    
def validate_length_min_max(input: str, min: int, max: int):
    if len(input) >= int(min) and len(input) <= int(max):
        return True
    else:
        return False
    
def validate_int_min_max(input: str, min: int, max: int):
    if not input.isnumeric():
        return False
    
    if int(input) >= int(min) and int(input) <= int(max):
        return True
    else:
        return False

def validate_date(input: str, format = "%d.%m.%Y"):
    try:
        datetime.strptime(input, format)
        return True
    except ValueError:
        return False

def get_selected_events(table: Treeview) -> list[Event]:
    results = []
    
    for focus_item in table.selection():
        table_item = table.item(focus_item)
        
        results.append(get_event_from_path(Path(table_item["values"][2])))
    
    return results

def delete_file(filepath: Path) -> None:
    if filepath.exists():
        remove(filepath.resolve())
    return

Logindaten = get_Logindaten()