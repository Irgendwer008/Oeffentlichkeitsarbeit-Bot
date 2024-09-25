# Oeffentlichkeitsarbeit-Bot
Ein Script zum automatischen Veröffentlichen der Veranstaltungen des Z10 e.V. auf Platformen aller Art

### Requirements

- Up to date **Python 3**

- **Selenium** is needed as it does all the web automation: `pip3 install selenium`

- **Firefox** is used as browser and therefor also necessary and has to be installed.

- locale **"de_DE"** is [installed](https://ubuntuforums.org/showthread.php?t=196414)

- **Nebenan.de** is set to **german locale** (I don't know if others are even possible, but still.)

### Allowed Image Files
- *.png
- *.jpg
- *.gif

### Currently fully working plugins:
- Kalender Karlsruhe
- Nebenan.de
- StuWe
- Z10 Website + Wiki

### Currently mostly working plugins:

### How to add new Plugins:
example with "Name" as plugin name:
- create a Name.py file that contains an object "plugininfo" of type "PluginInfo" (see helper.py) and a "run" funtion
- Set a friendly name (i.e. "my Plugin") and an dict[str: str] of category indices and names (if applicable, else leave empty)
- populate the run-function with code that logs into your platform and publishes the Event
- add the plugin to the "plugins" array in main ((currently) at line 114)

### Helpful links for further development
- [CSS Selectors](https://www.w3schools.com/cssref/css_selectors.php)
- [Nice overview over selenium and many of it's features](https://pythonexamples.org/python-selenium-introduction/)
- [datetime format codes](https://www.geeksforgeeks.org/python-datetime-strptime-function/)