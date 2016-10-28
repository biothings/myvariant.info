#!/usr/bin/env python

import sys
import os.path
import asyncio

def main(source):

    import biothings, config
    biothings.config_for_app(config)

    from biothings.dataload.uploader import SourceManager
    import dataload

    loop = biothings.get_loop()

    src_manager = SourceManager(loop)
    src_manager.register_source(source)
    jobs = src_manager.upload_src(source)

    loop.run_until_complete(asyncio.wait(jobs))

if __name__ == '__main__':
    # can pass "main_source" or "main_source.sub_source"
    main(sys.argv[1])
