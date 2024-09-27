# Oeffentlichkeitsarbeit-Bot
Ein Programm zum automatischen Veröffentlichen der Veranstaltungen des Z10 e.V. auf Platformen aller Art

``` sh
Benutzung: main.py [-h] [-w]

Automatisiertes Veröffentlichen von Events auf einer Reihe von Platformen

options:
  -h, --help          Zeige diese Hilfe und beende das Programm
  -w, --not-headless  Ist diese Flagge gesetzt öffnet sich Firefox als
                      Fenster. Wenn nicht, läuft es nur im Hintergrund
```


## Requirements for running executable

- The corresponding Binary File

- newest(-ish) version of Firefox installed

- a correctly filled "credentials.py" (For reference see credentials_template.py) in the same directory

- **Firefox** is used as browser and therefore also necessary and has to be installed.

- locale **"de_DE"** is installed ([Link for linux users](https://ubuntuforums.org/showthread.php?t=196414)).

- Firefox does not autotranslate Websites

## Requirements for running main.py

all pip-requirements are listed in requirements.txt. To install all at once execute `pip3 install -r requirements.txt`

- Up to date **Python 3**

- All needed file in the same structure as in this repo and a correctly filled "credentials.py" (For reference see credentials_template.py)

- **Selenium** is needed as it does all the web automation: `pip3 install selenium`

- **pwinput** is needed for the secret password prompt: `pip3 install pwinput`

- **Firefox** is used as browser and therefor also necessary and has to be installed.

- locale **"de_DE"** is [installed](https://ubuntuforums.org/showthread.php?t=196414)

- **Nebenan.de** is set to **german locale** (I don't know if others are even possible, but still.)

- Probably a linux distribution (tested only on Fedora 40). Maybe Windows, but i haven't tested yet. You are welcome to do so and report your findings!

## Create Executable from Python

Linux: `to_binary.sh`, Windows: `to_binary.bat`

### Requirements:

all pip-requirements are listed in requirements_for_binary_conversion.txt. To install all at once execute `pip3 install -r requirements.txt`

- Up to date **Python 3** (I assume)

- **Pyinstaller** is needed for the conversion: `pip3 install pyinstaller`

- **Firefox** is used as browser and therefor also necessary and has to be installed.

- Probably a linux distribution (tested only on Fedora 40). Maybe Windows, but i haven't tested yet. You are welcome to do so and report your findings!

### Allowed Image Files
- *.png
- *.jpg
- *.gif

### Currently fully working plugins:
- Kalender Karlsruhe
- Nebenan.de
- StuWe
- Z10 Website + Wiki
- Venyoo

### How to add new Plugins:
example with "Name" as plugin name:
- create a Name.py file that contains an object `plugininfo` of type `PluginInfo` (see helper.py) and a `run` funtion
- Set a `str` with a friendly name (i.e. "my Plugin"), a `str` of your default kategory key (if applicable, else `None`) and a `dict[str: str]` of category indices and names (if applicable, else a empty `dict`)
- populate the `run`-function with code that logs into your platform and publishes the Event
- import `Name` and add `Name` to the `plugins` array in main.py ((currently) at line 18)

### Helpful links for further development
This acts as a help for people new to this context, but also as a link-collection for future projects for myself
- [CSS Selectors](https://www.w3schools.com/cssref/css_selectors.php)
- [Nice overview over selenium and many of it's features](https://pythonexamples.org/python-selenium-introduction/)
- [datetime format codes](https://www.geeksforgeeks.org/python-datetime-strptime-function/)
- [Terminal Formating (colors etc.)](https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences)
- [Unicode box drawing](https://en.wikipedia.org/wiki/Box-drawing_characters)
