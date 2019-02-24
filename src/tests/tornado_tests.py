''' MyVariant Data-Aware Tests
    nosetests tornado_tests
    nosetests tornado_tests:MyVariantTestTornadoClient
'''

from tornado.web import Application

from biothings.tests.test_helper import TornadoTestServerMixin
from tests.tests import MyVariantTest
from web.settings import MyVariantWebSettings


class MyChemTestTornadoClient(TornadoTestServerMixin, MyVariantTest):
    '''
        Self contained test class, can be used for CI tools such as Travis
        Starts a Tornado server on its own and perform tests against this server.
    '''
    __test__ = True

    @classmethod
    def setup_class(cls):
        ''' Reads Tornado Settings from config.py '''
        cls.WEB_SETTINGS = MyVariantWebSettings(config='config')
        cls.APP_LIST = cls.WEB_SETTINGS.generate_app_list()
        cls.STATIC_PATH = cls.WEB_SETTINGS.STATIC_PATH

    def get_app(self):
        return Application(self.APP_LIST, static_path=self.STATIC_PATH)
