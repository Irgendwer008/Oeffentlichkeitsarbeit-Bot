from dataclasses import dataclass
from datetime import datetime, timedelta

YES = ["Y", "y", "Yes", "yes", "Ja", "ja"]
NO = ["N", "n", "No", "no", "Nein", "nein"]

@dataclass
class Veranstaltungsdetails:
    NAME: str 
    BESCHREIBUNG: str
    BEGINN: datetime
    BILD_DATEIPFAD: str
    ENDE: datetime = None # Optional
    UNTERÜBERSCHRIFT: str = "Eine Z10-e.V. Veranstaltung"
    ORT: str = "Zähringerstraße 10"
    LINK: str = "https://z10.info"
    AUSGEWÄHLTE_KATEGORIE: list[str] = "1444", "2" # Optional. For other Categories see the plugin's "pluginingo".

@dataclass
class PluginInfo:
    FRIENDLYNAME: str
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