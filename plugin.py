from dataclasses import dataclass
import ttkbootstrap as ttk
from my_dataclasses import Event
from selenium.webdriver import Firefox
from typing import Literal

# Adaptive import of credentials.py
from typing import TYPE_CHECKING
from publish import Publish
if TYPE_CHECKING:
    # Import template Logindaten only for type hinting (not at runtime)
    from credentials import Logindaten
else:
    from helper import Logindaten
    
@dataclass
class PluginInfo:
    FRIENDLYNAME: str
    DEFAULTCATEGORY_KEY: str
    KATEGORIEN: dict[str: str]

class Plugin():
    def __init__(self, plugininfo: PluginInfo):
        self.plugininfo = plugininfo
        
    def start(self, driver: Firefox, credentials: Logindaten, publisher: Publish):
        self.publisher = publisher
        raise NotImplementedError(f"Plugin {self.plugininfo.FRIENDLYNAME} is missing the required steps for login")
    
    def publish_events(self, driver: Firefox, eventlist: list[Event]):
        raise NotImplementedError(f"Plugin {self.plugininfo.FRIENDLYNAME} is missing the required steps for event publishing")
    
    def stop(self, driver: Firefox):
        raise NotImplementedError(f"Plugin {self.plugininfo.FRIENDLYNAME} is missing the required steps for closing up")
    
    def step(self, step: str, event: Event | Literal["All"]):
        self.publisher.status_update(self, step, event)
        
    def error(self, event: Event | Literal["All"]):
        self.publisher.status_error(self, event)
    
    def success(self, event: Event | Literal["All"]):
        self.publisher.status_success(self, event)