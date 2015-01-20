# -*- coding: utf-8 -*-

from .cosmic_parser import load_data as _load_data

COSMIC_INPUT_FILE = ''

def load_data():
    cosmic_data = _load_data(COSMIC_INPUT_FILE)
    return cosmic_data