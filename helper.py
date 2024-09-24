from dataclasses import dataclass
from datetime import datetime

@dataclass
class Veranstaltungsdetails:
    VERANSTALTUNG_NAME: str 
    VERANSTALTUNG_UNTERÜBERSCHRIFT: str 
    VERANSTALTUNG_BESCHREIBUNG: str  # Optional
    VERANSTALTUNG_BEGINN: datetime
    VERANSTALTUNG_BILD_DATEIPFAD: str
    VERANSTALTUNG_ENDE: datetime = None
    VERANSTALTUNG_ORT: str = "Zähringerstraße 10"
    VERANSTALTUNG_LINK: str = "https://z10.info"
    VERANSTALTUNG_BEREICH: str = "1444" # Optional: #1444 = Musik
                                                    #1445 = Theater, Tanz
                                                    #1443 = Literatur, Vorträge
                                                    #13 = Kunst, Ausstellungen
                                                    #10 = Architektur, Baukultur
                                                    #450664 = Wirtschaft, Wissenschaft
                                                    #7 = Messen, Kongresse
                                                    #6 = Stadtleben
                                                    #14 = Sport