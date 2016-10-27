#!/usr/bin/env python

import asyncio, asyncssh, sys
import concurrent.futures

executor = concurrent.futures.ProcessPoolExecutor()
loop = asyncio.get_event_loop()
loop.set_default_executor(executor)

import config, biothings
biothings.config_for_app(config)

import biothings.dataload.uploader as uploader
import dataload
manager = uploader.SourceManager(loop)
manager.register_sources(dataload.__sources_dict__)

COMMANDS = {
        "upload" : manager.upload_src,
        "upload_all": manager.upload_all,
        "manager" : manager
        }

passwords = {
        'guest': '', # guest account with no password
        }

from biothings.utils.hub import start_server

server = start_server(passwords=passwords,port=8022,commands=COMMANDS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

