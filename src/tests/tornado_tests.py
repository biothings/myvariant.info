import sys
import os

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from tests.tests_new import MyVariantTest
from biothings.tests.test_helper import TornadoRequestHelper
from www.api.handlers import return_applist
import unittest

class MyVariantTestTornadoClient(AsyncHTTPTestCase, MyVariantTest):
    __test__ = True

    def __init__(self, methodName='runTest', **kwargs):
        super(AsyncHTTPTestCase, self).__init__(methodName, **kwargs)
        self.h = TornadoRequestHelper(self)

    def get_app(self):
        return Application(return_applist())

if __name__ == "__main__":
    unittest.TextTestRunner().run(MyVariantTestTornadoClient.suite())
