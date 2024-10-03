from datetime import datetime
from datetime import timedelta
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *

from helper import Veranstaltungsdetails
    
# Plugin imports
import Plugins.KalenderKarlsruhe as KalenderKarlsruhe
import Plugins.Nebenande as Nebenande
import Plugins.StuWe as StuWe
import Plugins.Z10Website as Z10Website
import Plugins.Venyoo as Venyoo
available_plugins = [KalenderKarlsruhe, Nebenande, StuWe, Z10Website, Venyoo]

class MenuItem():
    def __init__(self, friendlyName: str, notebook:ttk.Notebook, buttonFrame) -> None:

        self.frame = ttk.Frame(notebook)
        self.frame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        notebook.add(self.frame, text=friendlyName)

        menuButton = ttk.Button(buttonFrame, text=friendlyName, command=lambda: notebook.select(self.frame))
        menuButton.pack(padx=5, pady=5)
        
        self.content()
        
    def content(self):
        pass
    
class NewEventItem(MenuItem):
    def __init__(self, friendlyName: str, notebook: ttk.Notebook, buttonFrame, available_plugins: list) -> None:
        self.available_plugins = available_plugins
        super().__init__(friendlyName, notebook, buttonFrame)
    
    def content(self):
        # Init the necessary variables
        self.plugins_list = []
        for plugin in available_plugins:
            self.plugins_list.append((plugin, ttk.BooleanVar(value=True)))
            
        self.title = ttk.StringVar()
        self.subtitle = ttk.StringVar()
        self.description = ttk.StringVar()
        self.start_hours = ttk.IntVar()
        self.start_minutes = ttk.IntVar()
        self.end_hours = ttk.IntVar()
        self.end_minutes = ttk.IntVar()
        
        
        # Scrollframe that contains all the elements
        scrollFrame = ScrolledFrame(self.frame, autohide=True)
        scrollFrame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        
        
        ## Input Elements
        
        # Plugins
        plugins_lbl = ttk.Label(scrollFrame, text="Plugins")
        plugins_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        plugins_frame = ttk.Frame(scrollFrame)
        plugins_frame.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        
        for tuple in self.plugins_list:
            ttk.Checkbutton(plugins_frame, onvalue=True, offvalue=False, text=tuple[0].plugininfo.FRIENDLYNAME, variable=tuple[1])\
                .pack(padx=5, pady=(5, 0), anchor=W)
        
        # Title
        title_lbl = ttk.Label(scrollFrame, text="Titel")
        title_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.title)
        title_en.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        
        # Subtitle
        title_lbl = ttk.Label(scrollFrame, text="Unterüberschrift")
        title_lbl.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.title)
        title_en.grid(row=2, column=1, padx=5, pady=5, sticky=EW)
        self.subtitle.set(Veranstaltungsdetails.UNTERÜBERSCHRIFT)
        
        # Description
        description_lbl = ttk.Label(scrollFrame, text="Beschreibung")
        description_lbl.grid(row=3, column=0, padx=5, pady=10, sticky=NW)
        description_txt = ttk.Text(scrollFrame, height=10)
        description_txt.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        
        # Start
        title_lbl = ttk.Label(scrollFrame, text="Veranstaltungsbeginn")
        title_lbl.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        start_frame = ttk.Frame(scrollFrame)
        start_frame.grid(row=4, column=1, sticky=W)
        
        ## Date
        date_entry = ttk.DateEntry(start_frame, firstweekday=0, dateformat="%d.%m.%Y")
        date_entry.pack(padx=5, pady=5, side=LEFT)

        ## Hours
        hours_spinbox = ttk.Spinbox(start_frame, from_=0, to=23, textvariable=self.start_hours, wrap=True, width=5)
        hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        self.start_hours.set((datetime.now() + timedelta(hours=1)).hour)
        
        ttk.Label(start_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        minutes_spinbox = ttk.Spinbox(start_frame, from_=0, to=59, textvariable=self.start_minutes, wrap=True, width=5)
        minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        
        ttk.Label(start_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        
        # End
        title_lbl = ttk.Label(scrollFrame, text="Veranstaltungsende")
        title_lbl.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        end_frame = ttk.Frame(scrollFrame)
        end_frame.grid(row=5, column=1, sticky=W)
        
        ## Date
        date_entry = ttk.DateEntry(end_frame, firstweekday=0, dateformat="%d.%m.%Y")
        date_entry.pack(padx=5, pady=5, side=LEFT)

        ## Hours
        hours_spinbox = ttk.Spinbox(end_frame, from_=0, to=23, textvariable=self.end_hours, wrap=True, width=5)
        hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        self.end_hours.set((datetime.now() + timedelta(hours=3)).hour)
        
        ttk.Label(end_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        minutes_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, textvariable=self.end_minutes, wrap=True, width=5)
        minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        
        ttk.Label(end_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        

# Main Window
root = ttk.Window(title="Z10 Autopublisher", themename="darkly")
# Start maximized
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

# Notebook, wich contains all the functionality of the program
tabs = ttk.Notebook(root)
tabs.pack(padx=5, pady=5, expand=True, fill=BOTH)

# The main-menu frame
mainMenuFrame = ttk.Frame(tabs)
mainMenuFrame.pack(padx=5, pady=5)
tabs.add(mainMenuFrame, text="Hauptmenü")

# A frame with for the buttons linking to the tabs
buttonFrame = ttk.Frame(mainMenuFrame)
buttonFrame.place(relx=0.5, rely=0.5, anchor=CENTER)

newEventItem = NewEventItem("Event erstellen", tabs, buttonFrame, available_plugins)

tabs.select(newEventItem.frame)

root.mainloop()