# -*- coding: utf-8 -*-

from .grasp_parser import load_data as _load_data

GRASP_INPUT_FILE = '/opt/myvariant.info/load_archive/grasp/GRASP2fullDataset'

def load_data():
    grasp_data = _load_data(GRASP_INPUT_FILE)
    return grasp_data
