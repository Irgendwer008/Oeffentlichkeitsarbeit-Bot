import ttkbootstrap as ttk
from my_dataclasses import PluginInfo

class pluginclass_for_publishing:
    def __init__(self, plugininfo: PluginInfo, checkbox: ttk.Checkbutton, label: ttk.Label, boolean_var: ttk.BooleanVar):
        self.plugininfo = plugininfo
        self.checkbox = checkbox
        self.label = label
        self.booleanvar = boolean_var