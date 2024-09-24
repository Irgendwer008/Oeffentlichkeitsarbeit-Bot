from dataclasses import dataclass

@dataclass
class Veranstaltungsdetails:
    VERANSTALTUNG_NAME: str 
    VERANSTALTUNG_UNTERÜBERSCHRIFT: str 
    VERANSTALTUNG_BESCHREIBUNG: str  # Optional
    VERANSTALTUNG_BEGINN_DATUM: str # Format: yyyy-mm-dd
    VERANSTALTUNG_BEGINN_ZEIT: str # Format: hh:mm
    VERANSTALTUNG_BILD_DATEIPFAD: str
    VERANSTALTUNG_ENDE_DATUM: str = "" # Format: yyyy-mm-dd
    VERANSTALTUNG_ENDE_ZEIT: str = "" # Format: hh:mm
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