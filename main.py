#!/usr/bin/env python

import argparse
from os import system
from types import ModuleType

system("")

# Allow command line argument handling before anything else
parser = argparse.ArgumentParser(
    description = "Automatisiertes Veröffentlichen von Events auf einer Reihe von Platformen",
    epilog = "Mehr auf Github: https://github.com/Irgendwer008/Oeffentlichkeitsarbeit-Bot")

parser.add_argument(
    "-w", 
    "--windowed", 
    dest="headless", 
    default=True, 
    action="store_false", 
    help="Ist diese Flagge gesetzt öffnet sich Firefox als Fenster. Wenn nicht, läuft es nur im Hintergrund")

parser.set_defaults(flag=True)
args = parser.parse_args()

# Auxiliary imports
from gui import MainWindow, EventListPage
    
# Plugin imports
import Plugins.KalenderKarlsruhe as KalenderKarlsruhe
import Plugins.Nebenande as Nebenande
import Plugins.StuWe as StuWe
import Plugins.Z10Website as Z10Website
import Plugins.Venyoo as Venyoo
available_plugins: list[ModuleType] = [KalenderKarlsruhe, Nebenande, StuWe, Z10Website, Venyoo]



#TODO: Check if events where published correctly (prob takes much time :,) )
#TODO: try facebok-sdk (see link at top of Meta.py)
#TODO: Get actual available categories from websites
#TODO: Add a lot of comments for better readability :D
#TODO: Add docstrings for better readability :D
#TODO: Venyoo working custom category
#TODO: Way to go back one step and change previous input
#TODO: Wrap Zeilen von langem Text in Beschreibung in Overview
#TODO: add credentials import from seperate file
#TODO: add argument implementation for credentials and image file
#TODO: Note necessary website locales in README.md
#TODO: Add python version check
#TODO: make all-plugins-button work
#TODO: Add Z10 Login check

if __name__ == "__main__":
    main_window = MainWindow()

    eventListPage = EventListPage(main_window, "Liste")

    main_window.root.mainloop()