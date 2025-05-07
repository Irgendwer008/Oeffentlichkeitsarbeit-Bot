from __future__ import annotations # to be able to avoid circular import of Plugin

from io import BytesIO
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.request import urlretrieve
from typing import TYPE_CHECKING

from credentials import Logindaten
from helper import pathify_event
from my_dataclasses import Event
# to avoid circular import
if TYPE_CHECKING:
    from plugin import Plugin 

# Import Logindaten only for type hinting (at runtime they are dynamically imported by helper.py)
if TYPE_CHECKING:
    from credentials import Logindaten
else:
    from helper import Logindaten

class Publish:
    def __init__(self, eventlist: list[Event], pluginlist: list[Plugin], headless: bool = True):
        self.eventlist = eventlist
        self.pluginlist = pluginlist
        
        # create gui
        self.window = ttk.Toplevel(title="Veröffentlichen...")
        
        self.treeview = ttk.Treeview(self.window, columns=("status"), style="Treeview")
        
        self.treeview.column('#0', anchor=W)
        self.treeview.column('status', anchor=W)
        
        self.treeview.heading('#0', text='Event', anchor=W)
        self.treeview.heading('status', text='Status', anchor=W)
        
        self.treeview.tag_configure("error", background="DarkRed")
        self.treeview.tag_configure("success", background="Green")

        self.treeview.pack(side=TOP, fill=BOTH, expand=True, padx=5)
        
        self.treeview_structure = {}
        
        for plugin_index in range(0, len(pluginlist)):
            publish_treeview_label = self.treeview.insert("", END, text=pluginlist[plugin_index].plugininfo.FRIENDLYNAME, open=True)
            
            publish_treeview_events = {}
            
            for event_index in range(0, len(eventlist)):
                index = self.treeview.insert(publish_treeview_label, END, text=eventlist[event_index].NAME, values=["Warte auf Begin"])
                publish_treeview_events.update({event_index: index})
            
            self.treeview_structure.update({plugin_index: publish_treeview_events})
            
        self.run(headless)
        
    
    def run(self, headless: bool = True):
        threads = []
        
        for plugin in self.pluginlist:
            thread = threading.Thread(target=self.run_plugin, args=(plugin, headless))
            threads.append(thread)
            self.window.after_idle(thread.start)

        for thread in threads:
            thread.join()
            
        self.window.destroy()
    
    def run_plugin(self, plugin: Plugin, headless: bool = True):
        
        credentials = Logindaten(Z10_USERNAME="", Z10_PASSWORD="")
        
        # init driver
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.set_preference("permissions.default.desktop-notification", 2)
        if headless:
            options.add_argument("--headless")
            
        driver = webdriver.Firefox(options=options)
    
        plugin.start(driver, credentials, self)
        plugin.publish_events(driver, self.eventlist)
        plugin.stop(driver)
        
        driver.quit()
    
    def status_update(self, plugin: Plugin, new_status: str, event: Event = None):
        tree = self.treeview
        
        def update_item(update_event: Event):
                item = self.treeview_structure[self.pluginlist.index(plugin)][self.eventlist.index(update_event)]
                self.window.after(0, lambda: tree.item(item, values=[new_status]))
        
        if event == "All":
            for event in self.eventlist:
                update_item(event)
        else:
            update_item(event)
    
    def status_error(self, plugin: Plugin, event: Event):
        tree = self.treeview
        
        def update_item(update_event: Event):
                item = self.treeview_structure[self.pluginlist.index(plugin)][self.eventlist.index(update_event)]
                self.window.after(0, lambda: tree.item(item, tags="error"))
        
        if event == "All":
            for event in self.eventlist:
                update_item(event)
        else:
            update_item(event)
        return
    
    def status_success(self, plugin: Plugin, event: Event):
        tree = self.treeview
        
        def update_item(update_event: Event):
                item = self.treeview_structure[self.pluginlist.index(plugin)][self.eventlist.index(update_event)]
                self.window.after(0, lambda: tree.item(item, tags="success"))
        
        if event == "All":
            for event in self.eventlist:
                update_item(event)
        else:
            update_item(event)
        return
        
        #self.event = event
        #
        #self.upload_image_filename = pathify_event(self.event).stem
        #
        #self._upload_to_nextcloud()
        #
        #print(self._check_successful_nextcloud_upload())
        #
        #self.credentials = self.get_credentials()
        
        #for plugin in available_plugins:
        #    plugin.
        
    #def _upload_to_nextcloud(self):
    #    path = Config.nextcloud_autopublisher_path
#
    #    nc = nc_py_api.Nextcloud(nextcloud_url=Config.nextcloud_url, nc_auth_user=Logindaten.Z10_USERNAME, nc_auth_pass=Logindaten.Z10_PASSWORD)
    #    buf = BytesIO()
    #    with Image.open(self.event.BILD_DATEIPFAD.resolve()) as img:
    #        img.save(buf, self.event.BILD_DATEIPFAD.suffix[1:])  # saving image to the buffer
    #    buf.seek(0)  # setting the pointer to the start of buffer
    #    nc.files.upload_stream(path + self.upload_image_filename, buf)  # uploading file from the memory to the user's root folder
    
    #def _check_successful_nextcloud_upload(self):
    #    
    #    download_url = f"{Config.nextcloud_url}/s/{Config.nextcloud_share_ID}/download?path=&files={self.upload_image_filename}"
    #    urlretrieve(download_url, self.upload_image_filename)
    #    
    #    return True