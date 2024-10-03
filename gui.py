from datetime import datetime
from datetime import timedelta
import os
from PIL import ImageTk, Image
from PyQt6.QtWidgets import QFileDialog, QApplication
import sys
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
        
os.environ['QT_QPA_PLATFORM'] = 'xcb'
qt_app = None

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
        self.plugins_list: list[list] = []
        for plugin in available_plugins:
            self.plugins_list.append([plugin, ttk.BooleanVar(value=True)]) # final form: [plugin, is plugin used?, plugin's combobox]
            
        self.title = ttk.StringVar()
        self.subtitle = ttk.StringVar()
        self.description = ttk.StringVar()
        self.start_hours = ttk.IntVar()
        self.start_minutes = ttk.IntVar()
        self.end_hours = ttk.IntVar()
        self.end_minutes = ttk.IntVar()
        self.location = ttk.StringVar()
        self.street = ttk.StringVar()
        self.zip = ttk.StringVar()
        self.city = ttk.StringVar()
        self.image_path = ttk.StringVar()
        self.link = ttk.StringVar()
        
        
        # Scrollframe that contains all the elements
        scrollFrame = ScrolledFrame(self.frame, autohide=True)
        scrollFrame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        
        
        ## Input Elements
        
        # Plugins
        plugins_lbl = ttk.Label(scrollFrame, text="Plugins")
        plugins_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        plugins_frame = ttk.Frame(scrollFrame)
        plugins_frame.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        
        plugins_all_cb = ttk.Checkbutton(plugins_frame, onvalue=True, offvalue=False, text="Alle")
        plugins_all_cb.pack(padx=5, pady=(5, 0), anchor=W)
        for item in self.plugins_list:
            ttk.Checkbutton(plugins_frame, onvalue=True, offvalue=False, text=item[0].plugininfo.FRIENDLYNAME, variable=item[1])\
                .pack(padx=5, pady=(5, 0), anchor=W)
        
        # Title
        title_lbl = ttk.Label(scrollFrame, text="Titel")
        title_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.title)
        title_en.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        
        # Subtitle
        title_lbl = ttk.Label(scrollFrame, text="Unterüberschrift")
        title_lbl.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.subtitle)
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
        self.start_hours.set(20)
        
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
        date_entry = ttk.DateEntry(end_frame, firstweekday=0, dateformat="%d.%m.%Y", startdate=datetime.today() + timedelta(days=1))
        date_entry.pack(padx=5, pady=5, side=LEFT)

        ## Hours
        hours_spinbox = ttk.Spinbox(end_frame, from_=0, to=23, textvariable=self.end_hours, wrap=True, width=5)
        hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        self.end_hours.set(1)
        
        ttk.Label(end_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        minutes_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, textvariable=self.end_minutes, wrap=True, width=5)
        minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        
        ttk.Label(end_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        
        # Location Name
        location_lbl = ttk.Label(scrollFrame, text="Veranstaltungsort")
        location_lbl.grid(row=6, column=0, padx=5, pady=5, sticky=W)
        location_en = ttk.Entry(scrollFrame, textvariable=self.location)
        location_en.grid(row=6, column=1, padx=5, pady=5, sticky=EW)
        self.location.set(Veranstaltungsdetails.LOCATION)
        
        
        # Address
        location_lbl = ttk.Label(scrollFrame, text="Addresse")
        location_lbl.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        address_frame = ttk.Frame(scrollFrame)
        address_frame.grid(row=7, column=1, sticky=EW)
        
        ## Street
        street_en = ttk.Entry(address_frame, textvariable=self.street)
        street_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        self.street.set(Veranstaltungsdetails.STRASSE)
        
        ttk.Label(address_frame, text=", ").pack(pady=5, side=LEFT)
        
        ## ZIP
        zip_en = ttk.Entry(address_frame, textvariable=self.zip, width=5)
        zip_en.pack(padx=5, pady=5, side=LEFT)
        self.zip.set(Veranstaltungsdetails.PLZ)
        
        ## City
        city_en = ttk.Entry(address_frame, textvariable=self.city)
        city_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        self.city.set(Veranstaltungsdetails.STADT)
        
        
        # Categories
        categories_lbl = ttk.Label(scrollFrame, text="Kategorien")
        categories_lbl.grid(row=8, column=0, padx=5, pady=10, sticky=NW)
        categories_frame = ttk.Frame(scrollFrame)
        categories_frame.grid(row=8, column=1, padx=5, pady=5, sticky=EW)
        categories_frame.columnconfigure(1, weight=1)

        for plugin_item in self.plugins_list:
            if plugin_item[0].plugininfo.DEFAULTCATEGORY_KEY is None:
                plugin_item.append(None)
            else:
                categories_plugin_lbl = ttk.Label(categories_frame, text=plugin_item[0].plugininfo.FRIENDLYNAME + ": ")
                categories_plugin_lbl.grid(row=self.plugins_list.index(plugin_item), column=0, padx=5, pady=(0, 5), sticky=W)
                categories_plugin_cb = ttk.Combobox(categories_frame, state=READONLY)
                categories_plugin_cb["values"] = list(plugin_item[0].plugininfo.KATEGORIEN.values())
                categories_plugin_cb.current(list(plugin_item[0].plugininfo.KATEGORIEN.keys()).index(plugin_item[0].plugininfo.DEFAULTCATEGORY_KEY))
                categories_plugin_cb.grid(row=self.plugins_list.index(plugin_item), column=1, padx=(5, 0), pady=(0, 5), sticky=EW)
                plugin_item.append(categories_plugin_cb)
        
        # Image
        image_lbl = ttk.Label(scrollFrame, text="Bild")
        image_lbl.grid(row=9, column=0, padx=5, pady=5, sticky=NW)
        image_frame = ttk.Frame(scrollFrame)
        image_frame.grid(row=9, column=1, padx=5, pady=5, sticky=EW)
        image_frame.columnconfigure(0, weight=1)
        
        image_lbl = ttk.Label(image_frame, textvariable=self.image_path, style="inverse-secondary")
        image_lbl.grid(row=0, column=0, sticky=NSEW, padx=5)
        
        image_preview = ttk.Label(image_frame)
        image_preview.grid(row=1, column=0, columnspan=2, sticky=W, padx=30, pady=30)
        
        def open_file_dialog():
            global qt_app
            if qt_app is None:
                qt_app = QApplication(sys.argv)
                
            file_name, _ = QFileDialog.getOpenFileName(None, "Bild auswählen", "", "Bilder (png oder jpg) (*.png *.jpg)")

            if file_name:
                img = Image.open(file_name)
                img.thumbnail((400, 200))
                img = ImageTk.PhotoImage(img)
                image_preview.config(image=img)
                image_preview.image = img # Necessary to keep image reference: https://web.archive.org/web/20201111190625/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
                self.image_path.set(file_name)
                
        image_btn = ttk.Button(image_frame, command=open_file_dialog, text="Datei auswählen")
        image_btn.grid(row=0, column=1, sticky=E)
        
        
        # Link
        title_lbl = ttk.Label(scrollFrame, text="Link")
        title_lbl.grid(row=10, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.link)
        title_en.grid(row=10, column=1, padx=5, pady=5, sticky=EW)
        self.link.set(Veranstaltungsdetails.LINK)
            
            

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