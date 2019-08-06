'''
    MyVariant Data-Aware Tests
'''

from nose.core import run

from biothings.tests import TornadoTestServerMixin
from tests.remote import MyVariantRemoteTest
from web.settings import MyVariantWebSettings


class MyVariantLocalTest(TornadoTestServerMixin, MyVariantRemoteTest):
    '''
        Self contained test class, can be used for CI tools such as Travis
        Starts a Tornado server on its own and perform tests against this server.
    '''

    # Override default setting loader
    settings = MyVariantWebSettings(config='config')


if __name__ == '__main__':
    print()
    print('MyVariant Local Test')
    print('-' * 70)
    print()
    run(argv=['', '--logging-level=INFO', '-v'], defaultTest='__main__.MyVariantLocalTest')
