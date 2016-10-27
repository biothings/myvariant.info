
# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.

import asyncio, asyncssh, crypt, sys

passwords = {'guest': '',                 # guest account with no password
            }

#def handle_session(stdin, stdout, stderr):
#    stdout.write('Welcome to my SSH server, %s!\n' %
#                 stdout.channel.get_extra_info('username'))
#    stdout.channel.exit(0)

loop = asyncio.get_event_loop()
import concurrent.futures
executor = concurrent.futures.ProcessPoolExecutor()#max_workers=15)
loop.set_default_executor(executor)

import config, biothings
biothings.config_for_app(config)
import biothings.dataload.uploader
import dataload
manager = biothings.dataload.uploader.SourceManager(loop)
manager.register_sources(dataload.__sources_dict__)

from IPython import InteractiveShell

import io


class MySSHServerSession(asyncssh.SSHServerSession):
    def __init__(self):
        self.shell = InteractiveShell(user_ns=globals())
        self._input = ''

    def connection_made(self, chan):
        self._chan = chan

        self.origout = sys.stdout
        self.buf = io.StringIO()
        print("redirect buf")
        sys.stdout = self.buf

        #self.origerr = sys.stderr
        #self.buferr = io.StringIO()
        #sys.stderr = self.buferr

    def shell_requested(self):
        return True

    def session_started(self):
        self._chan.write('Welcome to my SSH server, %s!\n' %
                          self._chan.get_extra_info('username'))
        self._chan.write('hub> ')

    def data_received(self, data, datatype):
        self._input += data

        lines = self._input.split('\n')
        for line in lines[:-1]:
            if not line:
                continue
            self.origout.write("run %s " % repr(line))
            r = self.shell.run_code(line)
            if r == 1:
                self.origout.write("Error\n")
                etype, value, tb = self.shell._get_exc_info(None)
                self._chan.write("Error: %s\n" % value)
            else:
                #self.origout.write(self.buf.read() + '\n')
                self.origout.write("OK\n")
                self.buf.seek(0)
                self._chan.write(self.buf.read())
                # clear buffer
                self.buf.seek(0)
                self.buf.truncate()
        self._chan.write('hub> ')

        self._input = lines[-1]

    def eof_received(self):
        self._chan.write('Have a good one...\n')
        self._chan.exit(0)

    def break_received(self, msec):
        # simulate CR
        self._chan.write('\n')
        self.data_received("\n",None)


class MySSHServer(asyncssh.SSHServer):

    def session_requested(self):
        return MySSHServerSession()

    def connection_made(self, conn):
        print('SSH connection received from %s.' %
                  conn.get_extra_info('peername')[0])

    def connection_lost(self, exc):
        if exc:
            print('SSH connection error: ' + str(exc), file=sys.stderr)
        else:
            print('SSH connection closed.')

    def begin_auth(self, username):
        # If the user's password is the empty string, no auth is required
        return passwords.get(username) != ''

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        pw = passwords.get(username, '*')
        return crypt.crypt(password, pw) == pw

async def start_server():
    await asyncssh.create_server(MySSHServer, '', 8022,
                                 server_host_keys=['bin/ssh_host_key'])

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

import asyncio, asyncssh, sys
