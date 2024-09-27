pyinstaller --onefile --distpath %~dp0/../ --clean --exclude-module credentials --name Oeffentlichkeitsarbeit-Bot-msys.exe %~dp0/../main.py
del Oeffentlichkeitsarbeit-Bot-msys.exe.spec