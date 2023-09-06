from pprint import pformat

from biothings.tests.web import BiothingsDataTest


class TestMyvariant(BiothingsDataTest):
    prefix = 'v1'
    host = 'myvariant.info'

    def check_index_count(self, assembly):
        # when run individually
        # it's possible there's not enough time to populate the metadata
        # before it is accessed
        # need a workaround #TODO
        meta = self.request(f"{assembly}/metadata").json()
        results = {}
        for src_name in meta["src"]:
            # if src_name == "cadd":
            #    continue
            if src_name == "snpeff":
                continue  # not a root src, counts always different
                # TODO: that said, count in meta could be correct...
            stats = meta["src"][src_name]["stats"]
            for stat in stats:
                subsrc = stat.replace("_%s" % assembly, "")
                if subsrc in ("gnomad_genomes", "gnomad_exomes"):
                    subsrc = subsrc.rstrip("s")  # plural in meta, singular in docs
                meta_cnt = meta["src"][src_name]["stats"][stat]
                try:
                    res = self.request("query?q=_exists_:%s&size=0&assembly=%s" %
                                       (subsrc, assembly)).json()
                except:
                    print(f'Query error for ("{subsrc}", "{assembly}")')
                    raise
                results[subsrc] = {"meta": meta_cnt, "index": res["total"]}
            #assert res["total"] == meta_cnt, "Count in metadata (%s) doesn't match count from query (%s) for datasource '%s'" % (meta_cnt,res["total"],subsrc)
        errs = {}
        for src in results:
            mc = results[src]["meta"]
            ic = results[src]["index"]
            if mc != ic:
                errs[src] = results[src]
                errs[src]["diff"] = mc - ic
        assert len(errs) == 0, "Some counts don't match metadata:\n%s" % pformat(errs)

    def test_300_metadata(self):
        self.request("metadata").content

    def test_301_fields(self):
        res = self.request('metadata/fields').json()
        # Check to see if there are enough keys
        assert len(res) > 480

        # Check some specific keys
        assert 'cadd' in res
        assert 'dbnsfp' in res
        assert 'dbsnp' in res
        assert 'wellderly' in res
        assert 'clinvar' in res

    def test_320_index_count_hg19(self):
        self.check_index_count("hg19")

    def test_321_index_count_hg38(self):
        self.check_index_count("hg38")
