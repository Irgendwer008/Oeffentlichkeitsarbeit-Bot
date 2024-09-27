DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
pyinstaller --onefile --distpath ../ --clean --exclude-module credentials --name Oeffentlichkeitsarbeit-Bot-$OSTYPE ${DIR%x}/../main.py
rm Oeffentlichkeitsarbeit-Bot-$OSTYPE.spec