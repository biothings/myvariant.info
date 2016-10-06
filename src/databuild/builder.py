
import biothings.databuild.builder as builder

class MyVariantDataBuilder(builder.DataBuilder):
    pass


if __name__ == '__main__':
    import sys

    import biothings, config
    biothings.config_for_app(config)
    from config import LOG_FOLDER

    import biothings.utils.mongo as mongo
    import biothings.databuild.backend as btbackend

    build_name = "myvariant"
    use_parallel = '-p' in sys.argv
    sources = None  # will build all sources
    target = None   # will generate a new collection name
    # "target_col:src_col1,src_col2" will specifically merge src_col1
    # and src_col2 into existing target_col (instead of merging everything)
    if not use_parallel and len(sys.argv) > 2:
        target,tmp = sys.argv[2].split(":")
        sources = tmp.split(",")

    # declare source backend
    source_backend =  btbackend.SourceDocMongoBackend(
                            build=mongo.get_src_build(),
                            master=mongo.get_src_master(),
                            dump=mongo.get_src_dump(),
                            sources=mongo.get_src_db())
    # declare target backend
    target_backend = btbackend.TargetDocMongoBackend(target_db=mongo.get_target_db())
    # assemble the whole
    bdr = MyVariantDataBuilder(
            build_name,
            doc_root_key=None,
            source_backend=source_backend,
            target_backend=target_backend,
            log_folder=config.LOG_FOLDER)
    # and start merging process
    bdr.merge(sources=sources,target_name=target)

