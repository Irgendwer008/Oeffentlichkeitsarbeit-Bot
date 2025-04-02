from datetime import datetime
from pathlib import Path
from PIL import ImageTk, Image
from tkinter.tix import Balloon
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import MessageDialog, Messagebox
from ttkbootstrap.icons import Icon
from yaml import dump

from helper import *
from my_dataclasses import Event, Config

from typing import TYPE_CHECKING, Literal
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
        
        self.event_frames: list[ViewEventPage] = []
        # Reference to events has to be kept so that their images stay in memory
        self.events = []
        
    def focus(self, id):
        frame = self.frames[id]
        frame.focus()
    
    def quit_program(self, _):
        self.root.destroy()
        
class Page():
    def __init__(self, main_window: MainWindow, friendly_name: str, side: Literal["left", "right", "top", "bottom"] = TOP) -> None:
        
        self.main_window = main_window

        self.page_frame = ttk.Frame(main_window.root)
        self.page_frame.pack(padx=5, pady=5, side=side, fill=BOTH, expand=True)
        
        self.populate_content()
        
    def populate_content(self):
        pass

class ListEventsPage(Page):
    def __init__(self, main_window, friendly_name: str = "Liste"):
        super().__init__(main_window, friendly_name)
    
    def populate_content(self):
        button_frame = ttk.Frame(self.page_frame)
        button_frame.pack(side=TOP, anchor=W, pady=(0, 5))
        
        self.refresh_button = IconButton(button_frame, text="Aktualisieren", file="icons/arrow-clockwise.png", command=self.refresh)
        self.open_button = IconButton(button_frame, text="Auswahl Öffnen", file="icons/pencil-square.png", command=self.open)
        self.self_button = IconButton(button_frame, text="Neues Event", file="icons/calendar-plus.png", command=self.new)
        self.delete_button = IconButton(button_frame, text="Auswahl Löschen", file="icons/trash-fill.png", command=self.delete)
        self.close_all_button = IconButton(button_frame, text="Alle Ansichten Schließen", file="icons/window-x.png", command=self.close_all)
        self.publish_button = IconButton(button_frame, text="Auswahl Veröffentlichen", file="icons/upload.png", command=self.publish)
        
        style = ttk.Style()  
        style.configure('Treeview', rowheight=50)  # increase height
        
        self.table = ttk.Treeview(self.page_frame, columns=("name", "start", "path", "image_path"), style="Treeview")
        self.table.bind("<Double-1>", self.open)
        self.table.bind("<Return>", self.open)
        
        self.table.column('#0', width=75, stretch=NO)
        self.table.column('name', anchor=W, width=100)
        self.table.column('start', anchor=W, width=100)
        self.table.column('path', anchor=W, width=500)
        self.table.column('image_path', anchor=W, width=500)
        
        self.table.heading('#0', text='', anchor=W)
        self.table.heading('name', text='Name', anchor=W)
        self.table.heading('start', text='Beginn', anchor=W)
        self.table.heading('path', text='Dateipfad', anchor=W)
        self.table.heading('image_path', text='Dateipfad Bild', anchor=W)
        
        self.table.tag_configure('oddrow', background='#292929')
        self.table.tag_configure('evenrow', background='#222222')

        self.table.pack(side=TOP, fill=BOTH, expand=True, padx=5)
        
        self.refresh()
        
    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        
        self.events = []
        
        file_list = get_list_of_eventfilepaths()
                
        for i in range(len(file_list)):
            event = get_event(file_list[i])
            
            self.main_window.events.append(event)
                
            formatted_data = [event.NAME, event.BEGINN.strftime("%d.%m.%Y, %H:%M"), event.DATEIPFAD, event.BILD_DATEIPFAD]
            
            event.img = Image.open(event.BILD_DATEIPFAD)
            event.img.thumbnail((50, 50))
            event.img = ImageTk.PhotoImage(event.img)
            
            if i % 2 == 0:
                self.table.insert(parent='', index="end", image=event.img, open=True, values=formatted_data, tags=('evenrow'))
            else:
                self.table.insert(parent='', index="end", image=event.img, open=True, values=formatted_data, tags=('oddrow'))

    def new(self):
        now = datetime.now()
        begin = datetime(now.year, now.month, now.day, now.hour, 0, 0)
        end = datetime(
            now.year,
            now.month,
            now.day if now.hour + 1 < 24 else now.day + 1,
            now.hour + 1 if now.hour + 1 < 24 else now.hour - 22,
            0,
            0)
        
        new_event = Event(
            DATEIPFAD=None,
            NAME="",
            BESCHREIBUNG="",
            BEGINN=begin,
            ENDE=end,
            BILD_DATEIPFAD=None,
            AUSGEWÄHLTE_KATEGORIE=None
        )
        
        ViewEventPage(self.main_window, new_event)

    def open(self, _ = None):
        for event in get_selected_events(self.table):            
            ViewEventPage(self.main_window, event)
    
    def close_all(self):
        for event_page in self.main_window.event_frames:
            event_page.cancel()
    
    def publish(self):
        pass
        #TODO
    
    def delete(self):
        events = get_selected_events(self.table)
        
        number_of_events = len(events)
        
        if not number_of_events:
            return
        
        message_string = ""
        
        if number_of_events == 1:
            message_string += f"Sollen neben dem Event \"{events[0].NAME}\" auch dessen Bild-Datei von diesem PC gelöscht werden?"
        elif number_of_events == 2:
            message_string += f"Sollen neben den Events \"{events[0].NAME}\" und \"{events[1].NAME}\" auch deren Bild-Dateien von diesem PC gelöscht werden?"
        elif number_of_events == 3:
            message_string += f"Sollen neben den Events \"{events[0].NAME}\", \"{events[1].NAME}\" und \"{events[2].NAME}\" auch deren Bild-Dateien von diesem PC gelöscht werden?"
        else:
            message_string += f"Sollen neben den Events \"{events[0].NAME}\", \"{events[1].NAME}\" und \"{events[2].NAME}\" und {number_of_events - 3} weiteren auch deren Bild-Dateien von diesem PC gelöscht werden?"
            
        match MessageDialog(message_string, "Löschen Bestätigen", buttons=["Abbrechen", "Nur Eventdateien:primary", "Events und Bilder"], icon=Icon.warning).show():
            case "Events und Bilder":
                for event in events:
                    delete_file(event.BILD_DATEIPFAD)
                    delete_file(event.DATEIPFAD)
            case "Nur Eventdateien":
                for event in events:
                    delete_file(event.DATEIPFAD)
        
        self.refresh()
        
        return

class ViewEventPage(Page):
    def __init__(self, main_window, event: Event, friendly_name: str = "Eventansicht"):
        self.event = event
        super().__init__(main_window, friendly_name, side=LEFT)
        self.page_frame.configure(height=self.main_window.root.winfo_height()*2/3)
        
        self.main_window.event_frames.append(self)
    
    def cancel(self):
        self.page_frame.destroy()
    
    def save(self):
        yaml_string = event_to_string(self.event)
        
        proposed_filepath = Path(pathify_event(self.event))
        
        if self.event.DATEIPFAD == None:
            for i in range(1, 100):
                if proposed_filepath.exists():
                    proposed_filepath = Path(pathify_event(self.event), i)
                if i == 100:
                    return FileExistsError("File creation was not possible")
            self.event.DATEIPFAD = proposed_filepath
        
        with open(self.event.DATEIPFAD, "w") as file:
            dump(yaml_string, file)
        
        Messagebox.show_info("Event erfolgreich gespeichert", "Speichern erfolgreich")
    
    def publish():
        pass
        #TODO
    
    def populate_content(self):
        # Init the necessary variables
        self.plugins_list = [] # final form: [plugin module, is plugin used? var, plugin's category combobox]
        for plugin in available_plugins:
            self.plugins_list.append([plugin, ttk.BooleanVar(value=True), None])
            
        self.title = ttk.StringVar(value=self.event.NAME)
        self.subtitle = ttk.StringVar(value=self.event.UNTERÜBERSCHRIFT)
        self.description = self.event.BESCHREIBUNG
        self.start_date = self.event.BEGINN
        self.start_hours = ttk.IntVar(value=self.event.BEGINN.hour)
        self.start_minutes = ttk.IntVar(value=self.event.BEGINN.minute)
        self.end_date = self.event.ENDE
        self.end_hours = ttk.IntVar(value=self.event.ENDE.hour)
        self.end_minutes = ttk.IntVar(value=self.event.ENDE.minute)
        self.location = ttk.StringVar(value=self.event.LOCATION)
        self.street = ttk.StringVar(value=self.event.STRASSE)
        self.zip = ttk.StringVar(value=self.event.PLZ)
        self.city = ttk.StringVar(value=self.event.STADT)
        self.image_path = ttk.StringVar(value=self.event.BILD_DATEIPFAD)
        self.link = ttk.StringVar(value=self.event.LINK)
        
        registered_validate_length_min_max = self.main_window.root.register(validate_length_min_max)
        registered_validate_int_min_max = self.main_window.root.register(validate_int_min_max)
        
        # Scrollframe that contains all the elements
        scrollFrame = ScrolledFrame(self.page_frame, autohide=True)
        scrollFrame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        
        ## Input Elements
        
        # Title
        title_lbl = ttk.Label(scrollFrame, text="Titel")
        title_lbl.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        title_en = ttk.Entry(scrollFrame, textvariable=self.title)
        title_en.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        title_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 60))
        
        # Subtitle
        subtitle_lbl = ttk.Label(scrollFrame, text="Unterüberschrift")
        subtitle_lbl.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        subtitle_en = ttk.Entry(scrollFrame, textvariable=self.subtitle)
        subtitle_en.grid(row=2, column=1, padx=5, pady=5, sticky=EW)
        subtitle_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 60))
        
        # Description
        description_lbl = ttk.Label(scrollFrame, text="Beschreibung")
        description_lbl.grid(row=3, column=0, padx=5, pady=10, sticky=NW)
        description_txt = ttk.Text(scrollFrame, height=10)
        description_txt.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        description_txt.insert("1.0", self.description)
        title_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 5000))
        
        # Start
        start_lbl = ttk.Label(scrollFrame, text="Veranstaltungsbeginn")
        start_lbl.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        start_frame = ttk.Frame(scrollFrame)
        start_frame.grid(row=4, column=1, sticky=W)
        
        ## Date
        start_dateEntry = ttk.DateEntry(start_frame, firstweekday=0, dateformat="%d.%m.%Y", startdate=self.start_date)
        start_dateEntry.pack(padx=5, pady=5, side=LEFT)

        ## Hours
        start_hours_spinbox = ttk.Spinbox(start_frame, from_=0, to=23, textvariable=self.start_hours, wrap=True, width=5)
        start_hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        start_hours_spinbox.config(validate="focusout", validatecommand=(registered_validate_int_min_max, "%P", 0, 23))
        
        ## ":"
        ttk.Label(start_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        start_minutes_spinbox = ttk.Spinbox(start_frame, from_=0, to=59, textvariable=self.start_minutes, wrap=True, width=5)
        start_minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        start_minutes_spinbox.config(validate="focusout", validatecommand=(registered_validate_int_min_max, "%P", 0, 59))
        
        ttk.Label(start_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        
        # End
        end_lbl = ttk.Label(scrollFrame, text="Veranstaltungsende")
        end_lbl.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        end_frame = ttk.Frame(scrollFrame)
        end_frame.grid(row=5, column=1, sticky=W)
        
        ## Date
        end_dateEntry = ttk.DateEntry(end_frame, firstweekday=0, dateformat="%d.%m.%Y", startdate=self.end_date)
        end_dateEntry.pack(padx=5, pady=5, side=LEFT)

        ## Hours
        end_hours_spinbox = ttk.Spinbox(end_frame, from_=0, to=23, textvariable=self.end_hours, wrap=True, width=5)
        end_hours_spinbox.pack(padx=5, pady=5, side=LEFT)
        end_hours_spinbox.config(validate="focusout", validatecommand=(registered_validate_int_min_max, "%P", 0, 23))
        
        ## ":"
        ttk.Label(end_frame, text=":").pack(padx=5, pady=5, side=LEFT)

        ## Minutes
        end_minutes_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, textvariable=self.end_minutes, wrap=True, width=5)
        end_minutes_spinbox.pack(padx=5, pady=5, side=LEFT)
        end_minutes_spinbox.config(validate="focusout", validatecommand=(registered_validate_int_min_max, "%P", 0, 59))
        
        ttk.Label(end_frame, text="Uhr").pack(padx=5, pady=5, side=LEFT)
        
        # Location Name
        location_lbl = ttk.Label(scrollFrame, text="Veranstaltungsort")
        location_lbl.grid(row=6, column=0, padx=5, pady=5, sticky=W)
        location_en = ttk.Entry(scrollFrame, textvariable=self.location)
        location_en.grid(row=6, column=1, padx=5, pady=5, sticky=EW)
        location_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 100))
        
        
        # Address
        location_lbl = ttk.Label(scrollFrame, text="Addresse")
        location_lbl.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        address_frame = ttk.Frame(scrollFrame)
        address_frame.grid(row=7, column=1, sticky=EW)
        
        ## Street
        street_en = ttk.Entry(address_frame, textvariable=self.street)
        street_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        street_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 60))
        
        ttk.Label(address_frame, text=", ").pack(pady=5, side=LEFT)
        
        ## ZIP
        zip_en = ttk.Entry(address_frame, textvariable=self.zip, width=5)
        zip_en.pack(padx=5, pady=5, side=LEFT)
        zip_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 5, 5))
        
        ## City
        city_en = ttk.Entry(address_frame, textvariable=self.city)
        city_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        city_en.config(validate="focusout", validatecommand=(registered_validate_length_min_max, "%P", 2, 60))
        
        
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
        try:
            img = Image.open(self.image_path.get())
            img.thumbnail((400, 200))
            img = ImageTk.PhotoImage(img)
            image_preview.config(image=img)
            image_preview.image = img # Necessary to keep image reference: https://web.archive.org/web/20201111190625/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
        except:
            pass
        
        def get_event_image_file():
            file_name = file_open_dialog("Bild öffnen", "Bilder (png oder jpg) (*.png *.jpg)")

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
        self.link.set(self.event.LINK)
        
        # Continue Buttons Frame
        continue_buttons_frame = ttk.Frame(self.page_frame)
        continue_buttons_frame.pack(padx=5, pady=5, fill=BOTH)
        
        cancel_btn = ttk.Button(continue_buttons_frame, text="Abbrechen", command=self.cancel)
        cancel_btn.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)
        
        save_btn = ttk.Button(continue_buttons_frame, text="Speichern", command=self.save)
        save_btn.grid(row=0, column=1, padx=5, pady=5, sticky=NSEW)
        
        publish_btn = ttk.Button(continue_buttons_frame, text="Veröffentlichen", command=self.publish)
        publish_btn.grid(row=0, column=2, padx=5, pady=5, sticky=NSEW)

"""

class NewEventMenu(MenuItem):
    def __init__(self, mainWindow: MainWindow) -> None:
        self.available_plugins = available_plugins
        self.mainWindow = mainWindow
        
        notebook = mainWindow.tabs
        buttonFrame = mainWindow.buttonFrame
        
        super().__init__(notebook, buttonFrame, friendly_name = "Event erstellen")
    
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
        self.sself.tablet = ttk.StringVar()
        self.zip = ttk.StringVar()
        self.city = ttk.StringVar()
        self.image_path = ttk.StringVar()
        self.link = ttk.StringVar()
        
        def validate_min_max(input, self.button, min, max):
            if len(input) >= min and len(input <= max):
                self.button.configure(bootstyle = SUCCESS)
                return True
            else:
                self.button.configure(bootstyle = WARNING)
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
        self.subtitle.set(my_dataclasses.UNTERÜBERSCHRIFT)
        
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
        self.location.set(my_dataclasses.LOCATION)
        
        
        # Address
        location_lbl = ttk.Label(scrollFrame, text="Addresse")
        location_lbl.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        address_frame = ttk.Frame(scrollFrame)
        address_frame.grid(row=7, column=1, sticky=EW)
        
        ## Sself.tablet
        sself.tablet_en = ttk.Entry(address_frame, textvariable=self.sself.tablet)
        sself.tablet_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        self.sself.tablet.set(my_dataclasses.STRASSE)
        
        ttk.Label(address_frame, text=", ").pack(pady=5, side=LEFT)
        
        ## ZIP
        zip_en = ttk.Entry(address_frame, textvariable=self.zip, width=5)
        zip_en.pack(padx=5, pady=5, side=LEFT)
        self.zip.set(my_dataclasses.PLZ)
        
        ## City
        city_en = ttk.Entry(address_frame, textvariable=self.city)
        city_en.pack(padx=5, pady=5, side=LEFT, fill=X, expand=True)
        self.city.set(my_dataclasses.STADT)
        
        
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
        self.link.set(my_dataclasses.LINK)
        
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
        details = my_dataclasses(NAME = self.title.get(), 
                                        UNTERÜBERSCHRIFT = self.subtitle.get(),
                                        BESCHREIBUNG = self.description.get(),
                                        BEGINN = datetime.strptime(self.start_entry.get() + self.start_hours + self.start_minutes, "%d.%m.%Y%-H%-M"),
                                        ENDE = datetime.strptime(self.end_entry.get() + self.end_hours + self.end_minutes, "%d.%m.%Y%-H%-M"),
                                        LOCATION = self.location.get(),
                                        STRASSE = self.sself.tablet.get(),
                                        PLZ = self.zip.get(),
                                        STADT = self.city.get(),
                                        BILD_DATEIPFAD = self.image_path.get(),
                                        LINK = self.link.get(),
                                        AUSGEWÄHLTE_KATEGORIE = selected_categories)
        
        # Enter necessary login credentials
        credentials = Logindaten(Z10_USERNAME = self.z10_username.get(),
                                Z10_PASSWORD = self.z10_password.get())
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
    
class PublishEventMenu(MenuItem):
    def __init__(self, mainWindow: MainWindow, available_plugins: list) -> None:
        self.available_plugins = available_plugins
        self.mainWindow = mainWindow
        
        super().__init__(notebook = mainWindow.tabs, buttonFrame = mainWindow.buttonFrame, friendly_name = "Event Hochladen")
"""

class IconButton():
    def __init__(self, master, text: str, file: str, command, side: Literal["left", "right", "top", "bottom"]=LEFT):
        self.master=master
        self.image = ttk.PhotoImage(file=file).subsample(2, 2)
        self.button = ttk.Button(master=master, text=text, image=self.image, command=command)
        self.button.pack(side=side, padx=5, pady=5, anchor=W)