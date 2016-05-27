import sys
import os

# Add this directory to python path (contains nosetest_config)
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from biothings.tests.tests import BiothingTests
from biothings.tests.settings import NosetestSettings
from nose.tools import ok_, eq_

ns = NosetestSettings()

class MyVariantTest(BiothingTests):
    __test__ = True # explicitly set this to be a test class
    # Add extra nosetests here
    pass

