
import biothings.databuild.builder as builder

class MyVariantDataBuilder(builder.DataBuilder):

    def post_merge(self):
        # MyVariant merging either insert or updates. So we can't just count
        # the number of inserted/updated data from single colleciton and compare with
        # the target count.
        total = sum(self.stats.values())
        self.logger.info("Validating...")
        target_cnt = self.target_backend.count()
        if total == 0:
            self.logger.warning("Nothing was inserted in target collection...")
        if target_cnt <= total:
            self.logger.info("OK [total count={} <= sum(total)={}]".format(target_cnt,total))
        else:
            self.logger.warning("Total count of documents {} is greater than what was inserted/updated... {}]".format(target_cnt, total))

