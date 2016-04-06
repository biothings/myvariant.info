# -*- coding: utf-8 -*-
# Simple template example used to instantiate a new biothing API
import sys
import os.path

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)

from biothings.www.index_base import main
from www.api.handlers import return_applist

if __name__ == '__main__':
    main(return_applist())