from dataclasses import dataclass

@dataclass
class Logindaten:
    # Z10
    Z10_USERNAME: str = "" # Leave empty, will be populated at runtime
    Z10_PASSWORD: str = "" # Leave empty, will be populated at runtime
    # Kalender Karlsruhe
    KALENDERKARLSRUHE_EMAIL: str = ""
    KALENDERKARLSRUHE_PASSWORD: str = ""
    # Nebenan.de
    NEBENANDE_EMAIL: str = ""
    NEBENANDE_PASSWORD: str = ""
    # Instagram (für Meta Business Suite)
    INSTAGRAM_USERNAME: str = ""
    INSTAGRAM_PASSWORD: str = ""
    # StuWe
    STUWE_USERNAME: str = ""
    STUWE_PASSWORD: str = ""
    # Venyoo
    VENYOO_USERNAME: str = ""
    VENYOO_PASSWORD: str = ""