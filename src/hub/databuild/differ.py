import config

from biothings.hub.dataexport.ids import export_ids, upload_ids
import biothings.hub.databuild.differ as differ
from biothings.utils.hub_db import get_src_build


class MyVariantDifferManager(differ.DifferManager):

     def post_publish(self, s3_folder, old_db_col_names, new_db_col_names, diff_folder,
                      release_folder, steps, s3_bucket, *args, **kwargs):
        bdoc = get_src_build().find_one({"_id" : new_db_col_names})
        assert bdoc, "Can't find build doc associated with index '%s' (should be named the same)" % new_db_col_names
        #ids_file = export_ids(new_db_col_names)
        ids_file = "/opt/variantdoc-hub/export/ids/hot_hg19_20180709_dm47vtlr_ids.xz"
        redir = "%s_ids.xz" % bdoc["build_config"]["assembly"]
        if "demo" in new_db_col_names:
            redir = "demo_%s" % redir
        upload_ids(ids_file, redir, 
                s3_bucket=config.IDS_S3_BUCKET,
                aws_key=config.AWS_KEY,
                aws_secret=config.AWS_SECRET)

