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
    KATEGORIE_KALENDERKARLSRUHE: int = 1444 # Optional. For other Categories see class "Kategorien" below.
    KATEGORIE_NEBENANDE: int = 2 # # Optional. For other Categories see class "Kategorien" below.

@dataclass
class Kategorien:
    KALENDERKARLSRUHE = {1444: "Musik",
                         1445: "Theater, Tanz",
                         1443: "Literatur, Vorträge",
                         13: "Kunst, Ausstellungen",
                         10: "Architektur, Baukultur",
                         450664: "Wirtschaft, Wissenschaft",
                         7: "Messen, Kongresse",
                         6: "Stadtleben",
                         14: "Sport"}
    
    NEBENANDE = ["Kennenlernen & Stammtische",
                 "Bildung & Erfahrung",
                 "Kunst, Kultur & Musik",
                 "Märkte & Flohmärkte",
                 "Familien & Kinder",
                 "Essen & Trinken",
                 "Feste & Feiern",
                 "Lokales Engagement",
                 "Gestalten & Heimwerken",
                 "Gesundheit & Wellness",
                 "Sport & Bewegung",
                 "Umwelt & Nachhaltigkeit",
                 "Teilen, Tauschen, Reparieren",
                 "Viertel verschönern",
                 "Ausflüge",
                 "Sonstiges"]
                                                    
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