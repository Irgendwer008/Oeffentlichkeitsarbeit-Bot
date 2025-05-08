from datetime import datetime
from pathlib import Path
from typing import Literal
from PIL import ImageTk, Image
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import MessageDialog, Messagebox
from ttkbootstrap.icons import Icon
from yaml import safe_dump

from helper import *
from my_dataclasses import Event
from plugin import Plugin
from publish import Publish

class MainWindow():
    def __init__(self, available_plugins: list[Plugin]):
        # Main Window
        self.root = ttk.Window(title="Z10 Autopublisher", themename="darkly")
        self.root.bind("<Control-q>", self.quit_program)
        
        # end maximized
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))
        
        self.available_plugins = available_plugins
        
        self.event_frames: list[ViewEventPage] = []
        # Reference to events has to be kept so that their images stay in memory
        self.events = []
        
        self.list_frame = ttk.Frame(self.root)
        self.view_frame = ttk.Frame(self.root)
        
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=3)
        
        self.list_frame.pack(padx=5, pady=5, fill=BOTH)
        self.view_frame.pack(padx=5, pady=5, fill=BOTH, expand=True)
        
        self.eventlist = EventList(self, self.list_frame)
        
    def focus(self, id):
        frame = self.frames[id]
        frame.focus()
    
    def quit_program(self, _):
        self.root.destroy()

class EventList():
    def __init__(self, main_window: MainWindow, frame: ttk.Frame):
        self.main_window = main_window
        self.frame = frame
        self.populate_content()

    def populate_content(self):
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side=TOP, anchor=W, pady=(0, 5))
        
        self.refresh_button = IconButton(button_frame, text="Aktualisieren", file="icons/arrow-clockwise.png", command=self.refresh)
        self.open_button = IconButton(button_frame, text="Auswahl Öffnen", file="icons/pencil-square.png", command=self.open)
        self.new_button = IconButton(button_frame, text="Neues Event", file="icons/calendar-plus.png", command=self.new)
        self.duplicate_button = IconButton(button_frame, text="Event Duplizieren", file="icons/copy.png", command=self.duplicate)
        self.delete_button = IconButton(button_frame, text="Auswahl Löschen", file="icons/trash-fill.png", command=self.delete)
        self.close_all_button = IconButton(button_frame, text="Alle Ansichten Schließen", file="icons/window-x.png", command=self.close_all)
        self.publish_button = IconButton(button_frame, text="Auswahl Veröffentlichen", file="icons/upload.png", command=self.publish)
        
        self.table = ttk.Treeview(self.frame, columns=("name", "end", "path", "image_path"), style="Treeview")
        self.table.bind("<Double-1>", self.open)
        self.table.bind("<Return>", self.open)
        
        self.style = ttk.Style()
        self.style.configure('Eventtable.Treeview', rowheight=50)  # increase height
        self.table.configure(style="Eventtable.Treeview")
        
        self.table.column('#0', width=75, stretch=False)
        self.table.column('name', anchor=W, width=100)
        self.table.column('end', anchor=W, width=100)
        self.table.column('path', anchor=W, width=500)
        self.table.column('image_path', anchor=W, width=500)
        
        self.table.heading('#0', text='', anchor=W)
        self.table.heading('name', text='Name', anchor=W)
        self.table.heading('end', text='Beginn', anchor=W)
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
            event = get_event_from_path(file_list[i])
            
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
        
        begin = datetime(
            now.year,
            now.month,
            now.day,
            now.hour,
            0,
            0)
        
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
        
        ViewEventPage(self.main_window, self.main_window.view_frame, self, new_event)

    def open(self, _ = None):
        selected = get_selected_events(self.table)
        
        if len(selected) == 0:
            return
        
        for event in selected:
            ViewEventPage(self.main_window, self.main_window.view_frame, self, event)

    def duplicate(self):
        
        selected = get_selected_events(self.table)
        
        if len(selected) == 0:
            return
        elif len(selected) > 1:
            Messagebox.show_info("Duplizieren von mehreren ausgewählten Events nicht möglich!", "Mehrfachauswahl ungültig")
            return
        else:
            pass
            #TODO

    def close_all(self):
        for event_page in self.main_window.event_frames:
            event_page.cancel()
    
    def publish(self):
        selected = get_selected_events(self.table)
        
        if len(selected) == 0:
            return
        
        PublishEventProcess(self.main_window, selected)
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
        
        messagebox = MessageDialog(message_string, "Löschen Bestätigen", buttons=["Abbrechen", "Nur Eventdateien:primary", "Events und Bilder"], icon=Icon.warning)
        messagebox.show()
        
        match messagebox.result:
            case "Events und Bilder":
                for event in events:
                    delete_file(event.BILD_DATEIPFAD)
                    delete_file(event.DATEIPFAD)
            case "Nur Eventdateien":
                for event in events:
                    delete_file(event.DATEIPFAD)
        
        self.refresh()
        
        return

class ViewEventPage():
    def __init__(self, main_window: MainWindow, frame: ttk.Frame, eventlist: EventList, event: Event):
        self.main_window = main_window
        all_events_frame = frame
        self.frame = ttk.Frame(all_events_frame)
        self.frame.pack(padx=5, pady=5, side=LEFT, fill="both", expand=True)
        self.event = event
        self.eventlist = eventlist
        
        self.main_window.event_frames.append(self)
        
        self.populate_content()
    
    def populate_content(self):
        # Init the necessary variables
        self.plugins_list: list[list[Plugin, ttk.Combobox]] = []
            
        self.title = ttk.StringVar(value=self.event.NAME)
        self.subtitle = ttk.StringVar(value=self.event.UNTERÜBERSCHRIFT)
        self.description = self.event.BESCHREIBUNG
        self.start_date = ttk.StringVar(value=self.event.BEGINN.strftime("%d.%m.%Y"))
        self.start_hours = ttk.IntVar(value=self.event.BEGINN.hour)
        self.start_minutes = ttk.IntVar(value=self.event.BEGINN.minute)
        self.end_date = ttk.StringVar(value=self.event.ENDE.strftime("%d.%m.%Y"))
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
        scrollFrame = ScrolledFrame(self.frame, autohide=True)
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
        self.description_txt = ttk.Text(scrollFrame, height=10)
        self.description_txt.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        self.description_txt.insert("1.0", self.description)
        
        # Start
        start_lbl = ttk.Label(scrollFrame, text="Veranstaltungsbeginn")
        start_lbl.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        start_frame = ttk.Frame(scrollFrame)
        start_frame.grid(row=4, column=1, sticky=W)
        
        ## Date
        start_dateEntry = ttk.DateEntry(start_frame, firstweekday=0, dateformat="%d.%m.%Y")
        start_dateEntry.pack(padx=5, pady=5, side=LEFT)
        start_dateEntry.entry.configure(textvariable=self.start_date)
        start_dateEntry.entry.configure(validatecommand=validate_date)

        # Hours
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
        end_dateEntry = ttk.DateEntry(end_frame, firstweekday=0, dateformat="%d.%m.%Y")
        end_dateEntry.pack(padx=5, pady=5, side=LEFT)
        end_dateEntry.entry.configure(textvariable=self.end_date)
        end_dateEntry.entry.configure(validatecommand=validate_date)

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
        
        for plugin in self.main_window.available_plugins:
            self.plugins_list.append([plugin])

        for plugin_item in self.plugins_list:
            if plugin_item[0].plugininfo.DEFAULTCATEGORY_KEY is not None:
                categories_plugin_lbl = ttk.Label(categories_frame, text=plugin_item[0].plugininfo.FRIENDLYNAME + ": ")
                categories_plugin_lbl.grid(row=self.plugins_list.index(plugin_item), column=0, padx=5, pady=(0, 5), sticky=W)
                categories_plugin_cb = ttk.Combobox(categories_frame, state=READONLY)
                categories_plugin_cb["values"] = list(plugin_item[0].plugininfo.KATEGORIEN.values())
                # set default value
                try:
                    for plugin_category in self.event.AUSGEWÄHLTE_KATEGORIE:
                        if plugin_category == plugin_item[0].plugininfo.FRIENDLYNAME:
                            possible_categories = list(plugin_item[0].plugininfo.KATEGORIEN.values())
                            selected_category = self.event.AUSGEWÄHLTE_KATEGORIE[plugin_category]
                            categories_plugin_cb.current(possible_categories.index(selected_category))
                except (TypeError, KeyError):
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
        continue_buttons_frame = ttk.Frame(self.frame)
        continue_buttons_frame.pack(padx=5, pady=5, fill=BOTH)
        
        cancel_btn = ttk.Button(continue_buttons_frame, text="Abbrechen / Schließen", command=self.cancel)
        cancel_btn.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)
        
        save_btn = ttk.Button(continue_buttons_frame, text="Speichern", command=self.save)
        save_btn.grid(row=0, column=1, padx=5, pady=5, sticky=NSEW)
        
        publish_btn = ttk.Button(continue_buttons_frame, text="Speichern & Veröffentlichen", command=self.publish)
        publish_btn.grid(row=0, column=2, padx=5, pady=5, sticky=NSEW)
    
    def cancel(self):
        self.frame.destroy()
    
    def save(self):
        #TODO: categories
        self.event.NAME = self.title.get()
        self.event.UNTERÜBERSCHRIFT = self.subtitle.get()
        self.event.BESCHREIBUNG = self.description_txt.get("1.0", END+"-1c").replace("\n\n", "\n\n\n")
        self.event.BEGINN = datetime.strptime(f"{self.start_date.get()}_{self.start_hours.get()}_{self.end_minutes.get()}", "%d.%m.%Y_%H_%M")
        self.event.ENDE = datetime.strptime(f"{self.end_date.get()}_{self.end_hours.get()}_{self.end_minutes.get()}", "%d.%m.%Y_%H_%M")
        self.event.LOCATION = self.location.get()
        self.event.STRASSE = self.street.get()
        self.event.PLZ = self.zip.get()
        self.event.STADT = self.city.get()
        self.event.BILD_DATEIPFAD = Path(self.image_path.get()).resolve() 
        categories = []
        for [plugin, checkbox] in self.plugins_list:
            categories.append([plugin.plugininfo.FRIENDLYNAME, checkbox.get()])
        self.event.AUSGEWÄHLTE_KATEGORIE = categories
        self.event.LINK = self.link.get()
        
        yaml_string = event_to_string(self.event)
        
        proposed_filepath = pathify_event(self.event)
                
        #TODO: Rework this check for old file paths as this probably doesn't work correctly        
        if self.event.DATEIPFAD == None:
            for i in range(1, 100):
                if proposed_filepath.exists():
                    proposed_filepath = pathify_event(self.event, i)
                    break
                if i == 100:
                    return FileExistsError("File creation was not possible")
        elif self.event.DATEIPFAD != proposed_filepath:
            delete_file(self.event.DATEIPFAD)
            self.event.DATEIPFAD = proposed_filepath
        
        self.event.DATEIPFAD = proposed_filepath
        
        with open(self.event.DATEIPFAD, "w") as file:
            safe_dump(yaml_string, file, sort_keys=False)
        
        Messagebox.show_info("Event erfolgreich gespeichert", "Speichern erfolgreich", position=(500, 500))
        
        self.cancel()
        self.eventlist.refresh()
    
    def publish(self):
        self.save()
        PublishEventProcess(self.main_window, [self.event])

class PublishEventProcess():
    def __init__(self, main_window: MainWindow, eventlist: list[Event]):
        self.main_window = main_window
        self.eventlist = eventlist

        self.eventlist_window = ttk.Toplevel(title="Veröffentlichen")
        self.eventlist_window.bind("<Control-q>", self.main_window.quit_program)

        # will launch a 900x400 window in the center of the main screen.
        #self.eventlist_window.geometry(center_window_to_display(self.eventlist_window, 900, 400))
        
        scrollFrame = ScrolledFrame(self.eventlist_window, autohide=True)
        scrollFrame.pack(padx=5, pady=5, expand=True, fill=BOTH)
        
        # Show overview of Events to be published
        table = ttk.Treeview(scrollFrame, columns=("name", "start", "end"), style="Eventtable.Treeview")
        table.pack(padx=5, pady=5, expand=True, fill=BOTH)
        
        table.column('#0', width=75, stretch=False)
        table.column('name', anchor=W, width=100)
        table.column('start', anchor=W, width=100)
        table.column('end', anchor=W, width=100)

        table.heading('#0', text='', anchor=W)
        table.heading('name', text='Name', anchor=W)
        table.heading('start', text='Beginn', anchor=W)
        table.heading('end', text='End', anchor=W)

        table.tag_configure('oddrow', background='#292929')
        table.tag_configure('evenrow', background='#222222')
        
        self.image_list = []
        
        for i in range(len(eventlist)):
            formatted_data = [eventlist[i].NAME, eventlist[i].BEGINN.strftime("%d.%m.%Y %H:%M"), eventlist[i].ENDE.strftime("%d.%m.%Y %H:%M")]
            
            img = Image.open(eventlist[i].BILD_DATEIPFAD)
            img.thumbnail((50, 50))
            img = ImageTk.PhotoImage(img)
            self.image_list.append(img) # keep reference to image
                 
            if i % 2 == 0:
                table.insert(parent='', index="end", image=img, open=True, values=formatted_data, tags=('evenrow'))
            else:
                table.insert(parent='', index="end", image=img, open=True, values=formatted_data, tags=('oddrow'))
        
        # Continue and cancel button
        button_frame = ttk.Frame(self.eventlist_window)
        button_frame.pack(padx=5, pady=5)
        
        continue_button = ttk.Button(button_frame, text="Bestätigen", command=self.run_plugin_selection)
        continue_button.pack(padx=5, pady=5, side=LEFT)
        
        cancel_button = ttk.Button(button_frame, text="Abbrechen", command=self.cancel)
        cancel_button.pack(padx=5, pady=5, side=LEFT)
        
    def run_plugin_selection(self):
        self.pluginlist_window = ttk.Toplevel(title="Platformauswahl")
        #self.pluginlist_window.geometry(center_window_to_display(self.pluginlist_window, 600, 300))
        self.pluginlist_window.bind("<Control-q>", self.main_window.quit_program)
        
        self.plugin_selection_list: list[list[Plugin, ttk.Checkbutton, ttk.Label, ttk.BooleanVar]] = []
        
        frame = ttk.Frame(self.pluginlist_window)
        frame.pack(padx=5, pady=5, expand=True, fill=Y)
        
        for plugin in self.main_window.available_plugins:
            plugininfo = plugin.plugininfo
            
            boolean_var = ttk.BooleanVar(value=True)
            
            checkbutton = ttk.Checkbutton(frame, bootstyle="success-round-toggle", variable=boolean_var)
            checkbutton.grid(row=self.main_window.available_plugins.index(plugin) + 1, column=0, padx=5, pady=5)
            
            label = ttk.Label(frame, text=plugininfo.FRIENDLYNAME)
            label.grid(row=self.main_window.available_plugins.index(plugin) + 1, column=1, sticky=NW, padx=5, pady=5)
            
            self.plugin_selection_list.append([plugin, checkbutton, label, boolean_var])
        
        self.check_all_bool = ttk.BooleanVar(value=True)
        check_all = ttk.Checkbutton(frame, variable=self.check_all_bool, bootstyle="round-toggle", command=self.check_all_update)
        check_all.grid(row=0, column=0)
            
        label_all = ttk.Label(frame, text="Alle")
        label_all.grid(row=0, column=1, pady=10)
        
        button_frame = ttk.Frame(self.pluginlist_window)
        button_frame.pack(padx=5, pady=5, side=BOTTOM)
            
        ttk.Button(button_frame, text="Weiter", command=self.ask_confirmation).pack(padx=5, pady=5, side=LEFT)
        ttk.Button(button_frame, text="Abbrechen", command=self.cancel).pack(padx=5, pady=5, side=LEFT)
        
    def check_all_update(self):
        if self.check_all_bool.get():
            for plugin in self.plugin_selection_list:
                plugin[3].set(True)
        else:
            for plugin in self.plugin_selection_list:
                plugin[3].set(False)
     
    def ask_confirmation(self):
        messagebox = MessageDialog("Sollen diese Events wirklich veröffentlicht werden? Achtung, dies kann nicht (einfach) rückgängig gemacht werden!",
                                   "Veröffentlichen Bestätigen",
                                   buttons=["Abbrechen",
                                            "Zurück",
                                            "Veröffentlichung Ausführen und dabei Browser Zeigen:danger",
                                            "Veröffentlichung Ausführen:danger"],
                                   icon=Icon.warning)
        messagebox.show()
        
        match messagebox.result:
                case "Abbrechen":
                    self.cancel()
                    
                case "Zurück":
                    pass
                    
                case "Veröffentlichung Ausführen und dabei Browser Zeigen":
                    plugins_to_publish_to: Plugin = []
                    
                    for item in self.plugin_selection_list:
                        plugins_to_publish_to.append(item[0])
                    
                    Publish(self.eventlist, plugins_to_publish_to, headless=False)
                
                case "Veröffentlichung Ausführen":
                    plugins_to_publish_to: Plugin = []
                    
                    for item in self.plugin_selection_list:
                        plugins_to_publish_to.append(item[0])
                    
                    Publish(self.eventlist, plugins_to_publish_to)
    
    def cancel(self):
        self.eventlist_window.destroy()
        try:
            self.pluginlist_window.destroy()
        except AttributeError:
            pass
       
class IconButton():
    def __init__(self, master, text: str, file: str, command, side: Literal["left", "right", "top", "bottom"]=LEFT):
        self.master=master
        self.image = ttk.PhotoImage(file=file).subsample(2, 2)
        self.button = ttk.Button(master=master, text=text, image=self.image, command=command)
        self.button.pack(side=side, padx=5, pady=5, anchor=W)