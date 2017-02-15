#!/usr/bin/env python

import sys
import asyncio

def main(source,**kwargs):

    import biothings, config
    biothings.config_for_app(config)

    from biothings.dataload.dumper import SourceManager
    import dataload

    loop = biothings.get_loop()

    src_manager = SourceManager(loop)
    src_manager.register_source(source)
    jobs = src_manager.dump_src(source,**kwargs)

    loop.run_until_complete(asyncio.wait(jobs))

if __name__ == '__main__':
    # can pass "main_source" or "main_source.sub_source"
    src = sys.argv[1]
    kwargs = dict(list(map(lambda e: e.split("="),sys.argv[2:])))
    main(src,**kwargs)
