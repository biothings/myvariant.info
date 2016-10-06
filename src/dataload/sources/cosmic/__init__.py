from .cosmic_parser import load_data as _load_data
from .cosmic_uploader import CosmicUploader
from .cosmic_dumper import CosmicDumper


def load_data():
    raise DeprecationWarning("Parser not active anymore, original data not available anymore")
    cosmic_data = _load_data(COSMIC_INPUT_FILE)
    return cosmic_data


