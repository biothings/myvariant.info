
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
manager = biothings.dataload.uploader.SourceManager(loop)
import dataload
manager.register_sources(dataload.__sources_dict__)

from IPython import InteractiveShell
shell = InteractiveShell(user_ns=globals())

import io



async def handle_session(stdin, stdout, stderr):
    stdout.write('Welcome to MyVariant hub, %s!\n\n' %
                 stdout.channel.get_extra_info('username'))

    def displayhook(obj):
        stdout.write(repr(obj))

    #stdin.channel.set_echo(False)
    while True:
        stdout.write('hub> ')
        secret = await stdin.readline()
        print(repr(secret))
        origout = sys.stdout
        origerr = sys.stderr
        #orighook, shell.displayhook = sys.displayhook, displayhook
        buf = io.StringIO()
        buferr = io.StringIO()
        sys.stdout = buf
        sys.stderr = buferr
        try:
            origout.write("run %s" % repr(secret))
            r = shell.run_code(secret)
            origout.write("r: %s" % repr(r))
            buf.seek(0)
            buferr.seek(0)
            if r == 1:
                origout.write("onela")
                shell.showtraceback()
                stderr.write("err: %s" % buferr.read())
            else:
                origout.write("onici")
                stdout.write(buf.read())
        finally:
            sys.stdout = origout
            sys.stderr = origerr
            #sys.displayhook = orighook

    stdin.channel.set_line_mode(False)
    stdout.write('\nYour secret is safe with me! Press any key to exit...')
    await stdin.read(1)

    stdout.write('\n')
    stdout.channel.exit(0)

class MySSHServer(asyncssh.SSHServer):
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
                                 server_host_keys=['bin/ssh_host_key'],
                                 session_factory=handle_session)

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()
