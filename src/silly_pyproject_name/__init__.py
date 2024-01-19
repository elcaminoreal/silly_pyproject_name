import importlib.metadata
from gather import entry

ENTRY_DATA = entry.EntryData.create(__name__)
__version__ = importlib.metadata.version(__name__)
