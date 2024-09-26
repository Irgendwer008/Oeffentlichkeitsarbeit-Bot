# Oeffentlichkeitsarbeit-Bot
Ein Script zum automatischen Veröffentlichen der Veranstaltungen des Z10 e.V. auf Platformen aller Art

### Requirements

all pip-requirements are listed in requirements.txt. To install all at once execute `pip3 install -r requirements.txt`

- Up to date **Python 3**

- **Selenium** is needed as it does all the web automation: `pip3 install selenium`

- **pwinput** is needed for the secret password prompt: `pip3 install pwinput`

- **Firefox** is used as browser and therefor also necessary and has to be installed.

- locale **"de_DE"** is [installed](https://ubuntuforums.org/showthread.php?t=196414)

- **Nebenan.de** is set to **german locale** (I don't know if others are even possible, but still.)

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

### Currently mostly working plugins:
None

### How to add new Plugins:
example with "Name" as plugin name:
- create a Name.py file that contains an object `plugininfo` of type `PluginInfo` (see helper.py) and a `run` funtion
- Set a `str` with a friendly name (i.e. "my Plugin"), a `str` of your default kategory key (if applicable, else `None`) and a `dict[str: str]` of category indices and names (if applicable, else a empty `dict`)
- populate the `run`-function with code that logs into your platform and publishes the Event
- import `Name` and add `Name` to the `plugins` array in main.py ((currently) at line 18)

### Helpful links for further development
- [CSS Selectors](https://www.w3schools.com/cssref/css_selectors.php)
- [Nice overview over selenium and many of it's features](https://pythonexamples.org/python-selenium-introduction/)
- [datetime format codes](https://www.geeksforgeeks.org/python-datetime-strptime-function/)