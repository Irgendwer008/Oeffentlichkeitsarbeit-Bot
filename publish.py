from io import BytesIO
import nc_py_api
from PIL import Image
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from credentials import Logindaten
from helper import pathify_event
from my_dataclasses import Event, Config

from typing import TYPE_CHECKING
# Import Logindaten only for type hinting (at runtime they are dynamically imported by helper.py)
if TYPE_CHECKING:
    from credentials import Logindaten
else:
    from helper import Logindaten
    
# Plugin imports
import Plugins.KalenderKarlsruhe as KalenderKarlsruhe
import Plugins.Nebenande as Nebenande
import Plugins.StuWe as StuWe
import Plugins.Z10Website as Z10Website
import Plugins.Venyoo as Venyoo
available_plugins = [KalenderKarlsruhe, Nebenande, StuWe, Z10Website, Venyoo]


class Publish:
    def __init__(self, event: Event):
        self.event = event
        self.upload_image_filename = pathify_event(self.event).stem
        
        self._upload_to_nextcloud()
        
        print(self._check_successful_nextcloud_upload())
        
        self.credentials = self.get_credentials()
        
    def _upload_to_nextcloud(self):
        path = Config.nextcloud_autopublisher_path

        nc = nc_py_api.Nextcloud(nextcloud_url=Config.nextcloud_url, nc_auth_user=Logindaten.Z10_USERNAME, nc_auth_pass=Logindaten.Z10_PASSWORD)
        buf = BytesIO()
        with Image.open(self.event.BILD_DATEIPFAD.resolve()) as img:
            img.save(buf, self.event.BILD_DATEIPFAD.suffix[1:])  # saving image to the buffer
        buf.seek(0)  # setting the pointer to the start of buffer
        nc.files.upload_stream(path + self.upload_image_filename, buf)  # uploading file from the memory to the user's root folder
    
    def _check_successful_nextcloud_upload(self):
        
        download_url = f"{Config.nextcloud_url}/s/{Config.nextcloud_share_ID}/download?path=&files={self.upload_image_filename}"
        urlretrieve(download_url, self.upload_image_filename)
        
        return True
    
    def get_credentials(_) -> Logindaten:
        # Enter necessary login credentials
        return Logindaten(Z10_USERNAME = "A",
                          Z10_PASSWORD = "B")
    
    def get_plugins(self):
        #TODO: update to gui version
        pass
        
        while True:
            # print all available plugins with number
            print("\n# Auf welchen Platformen soll die Veranstaltung veröffentlicht werden? Gib \"Alle\" wenn alle Plugins, oder die entsprechende(n) Zahl(en), mit Komma getrennt, an:\n")
            for i in range(1, len(available_plugins) + 1):
                print(" [" + str(i) + "] " + available_plugins[i-1].plugininfo.FRIENDLYNAME)
            
            # recieve answer
            answer = input("\n> ")
            
            # check, if "Alle" was selected
            if answer.lower() in ["alle", "allen", "all"]:
                self.plugins = available_plugins
            
            # if not, split the answer-string at every comma
            choices = answer.split(",")
                
            # Catch invalid input
            try:
                if len(choices) < 1:            # Catch no input
                    raise Exception
                
                choices = set(choices)          # remove duplicate numbers and sort
                    
                new_plugins_list = []
                
                for choice in choices:          # Iterate over every given choice
                    number = int(choice) - 1    # Catch choice not a integer
                    if number not in range(0, len(available_plugins)):    # Catch number out of range
                        raise Exception
                    new_plugins_list.append(available_plugins[number])
                
                self.plugins = new_plugins_list
                    
                    
            except:
                pass
            print(format.error("Deine Eingabe war fehlerhaft. Bitte versuche es erneut."))
    
    def run_plugins(self):
        
        # init driver    
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.set_preference("permissions.default.desktop-notification", 2)
        #TODO: add headless toggle
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        
        # Newline
        print("Publish")
        
        # Execute all the plugins
        try:
            lastsuccesful = 0
            for plugin in self.plugins:
                try:
                    plugin.run(self.event, self.credentials, self.plugins, driver)
                    print(format.GREEN +  "Veranstaltung erfolgreich auf " + self.plugins[lastsuccesful].plugininfo.FRIENDLYNAME + " veröffentlicht." + format.CLEAR)
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    print("\n\n" + str(e.with_traceback) + "\n\n")
                    print(format.error("Achtung \u26A0 Es gab einen Fehlers während des Hochladens auf \"" + self.plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
                lastsuccesful += 1
            driver.quit()
        except KeyboardInterrupt:
            print(format.error("Achtung \u26A0 Das Programm wurde vom Benutzer während des Hochladens auf \"" + self.plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
            driver.quit()
        except Exception as e:
            print(e)
            print(format.error("Achtung \u26A0 Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + self.plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + self.plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung veröffentlicht sein kann oder auch nicht!\n"))
            driver.quit()
            raise e
        
        driver.quit()