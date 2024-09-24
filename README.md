# Oeffentlichkeitsarbeit-Bot
Ein Script zum automatischen Veröffentlichen der Veranstaltungen des Z10 e.V. auf Platformen aller Art

### Requirements

- Up to date **Python 3**

- **Selenium** is needed as it does all the web automation: `pip3 install selenium`

- **Tkinter** is needed for file open dialog (should come preinstalled, if not, look [here](https://stackoverflow.com/questions/69603788/how-to-pip-install-tkinter))

- **Firefox** is used as browser and therefor also necessary and has to be installed.

- locale **"de_DE"** is [installed](https://ubuntuforums.org/showthread.php?t=196414)

- **Nebenan.de** is set to **german locale** (I don't know if others are even possible, but still.)

### Allowed Image Files
- *.png
- *.jpg
- *.gif

### Currently fully working plugins:
- KalenderKarlsruhe

### Currently mostly working plugins:
- Nebenan.de (category functionality missing, always "Kunst, Kultur und Musik")

### Helpful links for further development
- [CSS Selectors](https://www.w3schools.com/cssref/css_selectors.php)
- [Nice overview over selenium and many of it's features](https://pythonexamples.org/python-selenium-introduction/)
- [datetime format codes](https://www.geeksforgeeks.org/python-datetime-strptime-function/)