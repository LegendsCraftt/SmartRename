from PyQt6.QtCore import QSettings

settings = QSettings("TylerBuilds", "SmartRename")

# --- Defaults ---
DEFAULTS = {
    "removeStringsSaved": [],
    "removeStringsRecent": [],
    "removeSpaces": False,
}

# --- Core helpers ---
def save_setting(key, value):
    """Set and immediately sync a single setting."""
    settings.setValue(key, value)
    settings.sync()

def get_setting(key, default=None, type=None):
    """Fetch a setting with optional default/type safety."""
    if default is None:
        default = DEFAULTS.get(key)
    return settings.value(key, default, type=type)

def reset_setting(key):
    """Reset a specific setting to its default (if available)."""
    default = DEFAULTS.get(key)
    if default is not None:
        settings.setValue(key, default)
    settings.sync()

def reset_all_settings():
    """Reset all keys defined in DEFAULTS."""
    for key, default in DEFAULTS.items():
        settings.setValue(key, default)
    settings.sync()

# --- Convenience accessors ---
def get_saved_rm_strings():
    return get_setting("removeStringsSaved", [], type=list)

def get_recent_rm_strings():
    return get_setting("removeStringsRecent", [], type=list)

def add_saved_rm_string(string):
    """Insert a string into the saved list (most recent first)."""
    strings = get_saved_rm_strings()
    if string in strings:
        strings.remove(string)
    strings.insert(0, string)
    save_setting("removeStringsSaved", strings[:10])

def remove_saved_rm_string(string):
    """Remove a string from the saved list."""
    strings = get_saved_rm_strings()
    if string in strings:
        strings.remove(string)
        save_setting("removeStringsSaved", strings)

def edit_saved_rm_string(string, new_string):
    old_string = string
    remove_saved_rm_string(string)
    add_saved_rm_string(new_string)



def add_recent_rm_string(string):
    """Maintain a separate 'recent' list."""
    recents = get_recent_rm_strings()
    if string in recents:
        recents.remove(string)
    recents.insert(0, string)
    save_setting("removeStringsRecent", recents[:10])



