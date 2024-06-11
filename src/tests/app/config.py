
"""
    Config file to run tests for MyVariant.info
"""
import os as _os
import sys as _sys
import importlib.util as _imp_util

CONFIG_FILE_NAME = "config_web.py"

# find the path of the config file
_cur_dir = _os.path.dirname(_os.path.realpath(__file__))
_cfg_path = _os.path.abspath(_os.path.join(_cur_dir, CONFIG_FILE_NAME))
while True:
    if _os.path.exists(_cfg_path):
        break
    _new_path = _os.path.abspath(_os.path.join(
        _os.path.join(_os.path.dirname(_cfg_path), _os.path.pardir),
        CONFIG_FILE_NAME)
    )
    if _new_path == _cfg_path:
        raise Exception(f"no config file {CONFIG_FILE_NAME} found")
    else:
        _cfg_path = _new_path

# load config file using path
_spec = _imp_util.spec_from_file_location("parent_config", _cfg_path)
_config = _imp_util.module_from_spec(_spec)
_spec.loader.exec_module(_config)

# put the config variables into the module namespace
for _k, _v in _config.__dict__.items():
    if not _k.startswith('_'):
        globals()[_k] = _v

# insert module import path
_sys.path.insert(0, _os.path.dirname(_cfg_path))

# cleanup
del CONFIG_FILE_NAME

# override default
ES_HOST = 'http://localhost:9200'
ES_INDICES = {
    None: 'mvtest_hg19',
    'variant': 'mvtest_hg19',
    'hg19': 'mvtest_hg19',
    'hg38': 'mvtest_hg38'
}
ES_ARGS = {
    'request_timeout': 120,
}
