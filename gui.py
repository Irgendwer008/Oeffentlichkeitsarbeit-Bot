from datetime import datetime
from datetime import timedelta
from os import environ
from PIL import ImageTk, Image
from PyQt6.QtWidgets import QFileDialog, QApplication
from sys import exit, argv
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *

from helper import Veranstaltungsdetails
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Import Logindaten only for type hinting (not at runtime)
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

class MainWindow():
    def __init__(self):
        # Main Window
        self.root = ttk.Window(title="Z10 Autopublisher", themename="darkly")
        self.root.bind("<Control-q>", self.quit_program)
        
        # Start maximized
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))

        # Notebook, wich contains all the functionality of the program
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(padx=5, pady=5, expand=True, fill=BOTH)

        # The main-menu frame
        frame = ttk.Frame(self.tabs)
        frame.pack(padx=5, pady=5)
        self.tabs.add(frame, text="Hauptmenü")

        # A frame with for the buttons linking to the tabs
        self.buttonFrame = ttk.Frame(frame)
        self.buttonFrame.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    def quit_program(self):
        self.root.destroy()

class MenuItem():
    def __init__(self, notebook: ttk.Notebook, buttonFrame: ttk.Frame, friendlyName: str) -> None:

        self.frame = ttk.Frame(notebook)
        self.frame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        notebook.add(self.frame, text=friendlyName)

        menuButton = ttk.Button(buttonFrame, text=friendlyName, command=lambda: notebook.select(self.frame))
        menuButton.pack(padx=5, pady=5)
        
        self.content()
        
    def content(self):
        pass
    
class NewEventMenu(MenuItem):
    def __init__(self, mainWindow: MainWindow) -> None:
        self.available_plugins = available_plugins
        self.mainWindow = mainWindow
        
        notebook = mainWindow.tabs
        buttonFrame = mainWindow.buttonFrame
        
        super().__init__(notebook, buttonFrame, friendlyName = "Event erstellen")
    
    def file_open_dialog(self, title: str, filetypes: str, directory: str = "") -> str:
    
        environ['QT_QPA_PLATFORM'] = 'xcb'
        qt_app = None

        if qt_app is None:
            qt_app = QApplication(argv)
            
        file_name, _ = QFileDialog.getOpenFileName(None, title, directory, filetypes)
        
        return file_name
    
    def content(self):
        # Init the necessary variables
        self.plugins_list = [] # final form: [plugin module, is plugin used? var, plugin's category combobox]
        for plugin in available_plugins:
            self.plugins_list.append([plugin, ttk.BooleanVar(value=True), None])
            
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
        
        def validate_min_max(input, widget, min, max):
            if len(input) >= min and len(input <= max):
                widget.configure(bootstyle = SUCCESS)
                return True
            else:
                widget.configure(bootstyle = WARNING)
                return False
                
            
        
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
        title_en.config(validate="focusout", validatecommand=(validate_min_max, "%P", title_en, 2, 5000))
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
        start_lbl = ttk.Label(scrollFrame, text="Veranstaltungsbeginn")
        start_lbl.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        start_frame = ttk.Frame(scrollFrame)
        start_frame.grid(row=4, column=1, sticky=W)
        
        ## Date
        start_dateEntry = ttk.DateEntry(start_frame, firstweekday=0, dateformat="%d.%m.%Y")
        start_dateEntry.pack(padx=5, pady=5, side=LEFT)
        self.start_entry = start_dateEntry.entry

        ## Hours
        start_hours_spinbox = ttk.Spinbox(start_frame, from_=0, to=23, textvariable=self.start_hours, wrap=True, width=5)
        start_hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        self.start_hours.set(20)
        
        ttk.Label(start_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        minutes_spinbox = ttk.Spinbox(start_frame, from_=0, to=59, textvariable=self.start_minutes, wrap=True, width=5)
        minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        
        ttk.Label(start_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        
        # End
        end_lbl = ttk.Label(scrollFrame, text="Veranstaltungsende")
        end_lbl.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        end_frame = ttk.Frame(scrollFrame)
        end_frame.grid(row=5, column=1, sticky=W)
        
        ## Date
        end_dateEntry = ttk.DateEntry(end_frame, firstweekday=0, dateformat="%d.%m.%Y", startdate=datetime.today() + timedelta(days=1))
        end_dateEntry.pack(padx=5, pady=5, side=LEFT)
        self.end_entry = end_dateEntry.entry

        ## Hours
        end_hours_spinbox = ttk.Spinbox(end_frame, from_=0, to=23, textvariable=self.end_hours, wrap=True, width=5)
        end_hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        self.end_hours.set(1)
        
        ttk.Label(end_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        end_minutes_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, textvariable=self.end_minutes, wrap=True, width=5)
        end_minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        
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
            if plugin_item[0].plugininfo.DEFAULTCATEGORY_KEY is not None:
                categories_plugin_lbl = ttk.Label(categories_frame, text=plugin_item[0].plugininfo.FRIENDLYNAME + ": ")
                categories_plugin_lbl.grid(row=self.plugins_list.index(plugin_item), column=0, padx=5, pady=(0, 5), sticky=W)
                categories_plugin_cb = ttk.Combobox(categories_frame, state=READONLY)
                categories_plugin_cb["values"] = list(plugin_item[0].plugininfo.KATEGORIEN.values())
                categories_plugin_cb.current(list(plugin_item[0].plugininfo.KATEGORIEN.keys()).index(plugin_item[0].plugininfo.DEFAULTCATEGORY_KEY))
                categories_plugin_cb.grid(row=self.plugins_list.index(plugin_item), column=1, padx=(5, 0), pady=(0, 5), sticky=EW)
                plugin_item[2] = categories_plugin_cb
        
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
        
        def get_event_image_file():
            file_name = self.file_open_dialog("Bild öffnen", "Bilder (png oder jpg) (*.png *.jpg)")

            if file_name:
                img = Image.open(file_name)
                img.thumbnail((400, 200))
                img = ImageTk.PhotoImage(img)
                image_preview.config(image=img)
                image_preview.image = img # Necessary to keep image reference: https://web.archive.org/web/20201111190625/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
                self.image_path.set(file_name)
                
        image_btn = ttk.Button(image_frame, command=get_event_image_file, text="Datei auswählen")
        image_btn.grid(row=0, column=1, sticky=E)
        
        
        # Link
        link_lbl = ttk.Label(scrollFrame, text="Link")
        link_lbl.grid(row=10, column=0, padx=5, pady=5, sticky=W)
        link_en = ttk.Entry(scrollFrame, textvariable=self.link)
        link_en.grid(row=10, column=1, padx=5, pady=5, sticky=EW)
        self.link.set(Veranstaltungsdetails.LINK)
        
        # Confirm Button
        confirm_btn = ttk.Button(scrollFrame, text="Bestätigen", command=lambda: self.Z10_login())
        confirm_btn.grid(row=11, column=0, columnspan=2, sticky=NE)

    def Z10_login(self):
        
        try:
            for plugin_item in self.plugins_list:
                if plugin_item[0] is Z10Website:
                    if plugin_item[1].get() == False:
                        self.publish_event()
                        return
                    else:
                        self.z10_username = ttk.StringVar()
                        self.z10_password = ttk.StringVar()
                        
                        login_root = ttk.Toplevel("Z10 Login")
                        self.mainWindow.root.eval(f'tk::PlaceWindow {str(login_root)} center')
                    
                        # Username
                        username_lbl = ttk.Label(login_root, text="Kürzel")
                        username_lbl.grid(row=0, column=0, padx=5, pady=5)
                        username_en = ttk.Entry(login_root)
                        username_en.grid(row=0,  column=1, padx=5, pady=5)
                        
                        # Password
                        username_lbl = ttk.Label(login_root, text="Passwort")
                        username_lbl.grid(row=1, column=0, padx=5, pady=5)
                        username_en = ttk.Entry(login_root, show="*")
                        username_en.grid(row=1,  column=1, padx=5, pady=5)
                        
                        # Confirm button
                        confirm_btn = ttk.Button(login_root, text="Bestätigen", command=lambda: self.publish_event(login_root))
                        confirm_btn.grid(row=2, column=1, padx=5, pady=5, sticky=E)
                        
            login_root.mainloop()
            
        except NameError:
            self.publish_event()
        
    def publish_event(self, toplevel_to_destroy: ttk.Toplevel = None):
        
        if toplevel_to_destroy is not None: 
            toplevel_to_destroy.destroy()
        
        selected_plugins = []
        selected_categories = []
        
        for pluginitem in self.plugins_list:
            print(pluginitem[0])
            print(pluginitem[1].__class__)
            print(pluginitem[1].__class__)
            print("")
            if pluginitem[1].get(): # Get state of respective BooleanVar (set by the checkboxes)
                selected_plugins.append(pluginitem[0])
                selected_categories.append(list(pluginitem[0].plugininfo.KATEGORIEN.keys())[pluginitem[2].current()])

        # Set event details
        details = Veranstaltungsdetails(NAME = self.title.get(), 
                                        UNTERÜBERSCHRIFT = self.subtitle.get(),
                                        BESCHREIBUNG = self.description.get(),
                                        BEGINN = datetime.strptime(self.start_entry.get() + self.start_hours + self.start_minutes, "%d.%m.%Y%-H%-M"),
                                        ENDE = datetime.strptime(self.end_entry.get() + self.end_hours + self.end_minutes, "%d.%m.%Y%-H%-M"),
                                        LOCATION = self.location.get(),
                                        STRASSE = self.street.get(),
                                        PLZ = self.zip.get(),
                                        STADT = self.city.get(),
                                        BILD_DATEIPFAD = self.image_path.get(),
                                        LINK = self.link.get(),
                                        AUSGEWÄHLTE_KATEGORIE = selected_categories)
        
        # Enter necessary login credentials
        credentials = Logindaten(Z10_USERNAME = self.z10_username.get(),
                                Z10_PASSWORD = self.z10_password.get())
        """
        # init driver    
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.set_preference("permissions.default.desktop-notification", 2)
        if args.headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        
        # Newline
        print("Publish")
        
        # Execute all the plugins
        try:
            lastsuccesful = 0
            for plugin in plugins:
                try:
                    plugin.run(details, credentials, plugins, driver)
                    print(format.GREEN +  "Veranstaltung erfolgreich auf " + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + " veröffentlicht." + format.CLEAR)
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    print("\n\n" + str(e.with_traceback) + "\n\n")
                    print(format.error("Achtung \u26A0 Es gab einen Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
                lastsuccesful += 1
            driver.quit()
        except KeyboardInterrupt:
            print(format.error("Achtung \u26A0 Das Programm wurde vom Benutzer während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die Platformen manuell, da die Veranstaltung hier höchstwahrscheinlich nicht veröffentlicht werden konnte!\n"))
            driver.quit()
        except Exception as e:
            print(e)
            print(format.error("Achtung \u26A0 Das Programm wurde aufgrund eines Fehlers während des Hochladens auf \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\" unterbrochen! Bitte überprüfe die einzelnen Platformen manuell, besonders \"" + plugins[lastsuccesful].plugininfo.FRIENDLYNAME + "\", da die Veranstaltung veröffentlicht sein kann oder auch nicht!\n"))
            driver.quit()
            raise e
        
        driver.quit()
"""
    
class PublishEventMenu(MenuItem):
    def __init__(self, mainWindow: MainWindow, available_plugins: list) -> None:
        self.available_plugins = available_plugins
        self.mainWindow = mainWindow
        
        super().__init__(notebook = mainWindow.tabs, buttonFrame = mainWindow.buttonFrame, friendlyName = "Event Hochladen")