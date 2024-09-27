DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
DIR="${DIR%x}"
echo $DIR
pyinstaller --onefile --distpath ./ --clean --exclude-module credentials --add-data "credentials.py:." --name "Oeffentlichkeitsarbeit-Bot-$OSTYPE" "$DIR/main.py"
