#!/usr/bin/env python

import asyncio
import sys
import json

def main(build_name,**kwargs):

    import biothings, config
    biothings.config_for_app(config)
    import biothings.databuild.builder as builder
    from databuild.builder import MyVariantDataBuilder

    loop = biothings.get_loop()

    bmanager = builder.BuilderManager(builder_class=MyVariantDataBuilder,event_loop=loop)
    bmanager.sync() # grab build configs
    job = bmanager.merge(build_name,**kwargs)
    loop.run_until_complete(job)


if __name__ == '__main__':
    build_name = sys.argv[1]
    # treat other args as python kwargs (value as json string)
    skwargs = sys.argv[2:]
    kwargs = {}
    for k,v in map(lambda e: e.split("="),skwargs):
        kwargs[k] = json.loads(v)
    main(build_name,**kwargs)
