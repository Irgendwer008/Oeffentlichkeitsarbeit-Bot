from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Event:
    DATEIPFAD:str
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