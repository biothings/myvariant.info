from time import sleep
from urllib.parse import urljoin

from biothings.tests.web import BiothingsWebAppTest


class TestMetadataAssemblyAware(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'mv_app_test'

    def test_metadata_source_assembly(self):
        metadata_url = f'{self.prefix}/' + 'metadata/fields'
        res_default = self.request(metadata_url)
        res_hg19 = self.request(metadata_url, params={'assembly': 'hg19'})
        res_hg38 = self.request(metadata_url, params={'assembly': 'hg38'})
        assert res_default.json() == res_hg19.json()
        assert res_hg19.json() != res_hg38.json()  # I am not certain this will hold true

    def test_metadata_field_assembly(self):
        metadata_url = f'{self.prefix}/' + 'metadata'
        res_default = self.request(metadata_url)
        res_hg19 = self.request(metadata_url, params={'assembly': 'hg19'})
        res_hg38 = self.request(metadata_url, params={'assembly': 'hg38'})
        assert res_default.json() == res_hg19.json()
        assert res_hg19.json() != res_hg38.json()  # I am not certain this will hold true


class TestAnnotationFields(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'mv_app_test'

    def test_id_variant(self):
        variant = 'chr8:g.7194707G>A'
        res = self.request('variant', data={'id': variant})
        assert res.json()['_id'] == variant

    def test_id_hg19(self):
        variant = 'chr8:g.7194707G>A'
        res = self.request('hg19', data={'id': variant})
        assert res.json()['_id'] == variant

    def test_id_hg38(self):
        variant = 'chrX:g.30718532C>T'
        res = self.request('hg38', data={'id': variant})
        assert res.json()['_id'] == variant

    def test_clingen_caid(self):
        # FIXME: this field is not found
        pass

    def test_rsid(self):
        variant = 'rs771931171'
        res = self.request('variant', data={'id': variant})
        assert self.value_in_result(variant, res.json(), 'dbsnp.rsid',
                                    case_insensitive=True)

    def test_rsid_ci(self):
        variant = 'rS771931171'
        res = self.request('variant', data={'id': variant})
        assert self.value_in_result(variant, res.json(), 'dbsnp.rsid',
                                    case_insensitive=True)

    def test_rcv_id(self):
        variant = 'RCV000665743'
        res = self.request('variant', data={'id': variant})
        assert self.value_in_result(variant, res.json(), 'clinvar.rcv.accession',
                                    case_insensitive=True)
    def test_rcv_id_ci(self):
        variant = 'rCv000665743'
        res = self.request('variant', data={'id': variant})
        assert self.value_in_result(variant, res.json(), 'clinvar.rcv.accession',
                                    case_insensitive=True)

    def test_ftid(self):
        # also tests using hg38 as an argument to assembly
        variant = 'VAR_062998'
        res = self.request('variant', data={'id': variant, 'assembly': 'hg38'})
        assert self.value_in_result(variant, res.json(), 'uniprot.humsavar.ftid',
                                    case_insensitive=True)

    def test_ftid_ci(self):
        variant = 'var_062998'
        res = self.request('variant', data={'id': variant, 'assembly': 'hg38'})
        assert self.value_in_result(variant, res.json(), 'uniprot.humsavar.ftid',
                                    case_insensitive=True)


class TestRedirecdt(BiothingsWebAppTest):
    def test_redir_1_expected(self):
        # Not entirely sure what this is supposed to do
        res = self.request('/v1/variant/chr8:7194707G>A', expect=301,
                           allow_redirects=False)
        assert res.headers['location'] == '/v1/variant/chr8:g.7194707G>A'

    def test_redir_2(self):
        res = self.request('/v1/variant/chr99:..1test', expect=301,
                           allow_redirects=False)
        assert res.headers['location'] == '/v1/variant/chr99:g.1test'

    def test_redir_3(self):
        res = self.request('/v1/variant/chr1:gg1test', expect=301,
                           allow_redirects=False)
        assert res.headers['location'] == '/v1/variant/chr1:g.1test'

    def test_redir_4(self):
        res = self.request('/v1/variant/chrTM:.g1test', expect=301,
                           allow_redirects=False)
        assert res.headers['location'] == '/v1/variant/chrTM:g.1test'

    def test_redir_not(self):
        # we don't have ES for this test class, expect 500
        self.request('/v1/variant/chr8:g.7194707G>A', expect=500,
                     allow_redirects=False)


class TestLicenseXfrm(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'mv_app_test'

    def _wait(self):
        # seems like the only way to do it
        # although this is not its (AsyncTestCase.wait) intended use
        # (besides actually fixing the issue so that web blocks until metadata is ready)
        #
        # Note: don't try to put it in a fixture, it won't work
        try:
            self.wait(timeout=3.0)
        except:  # noqa
            pass

    def test_exac_nontcga(self):
        self._wait()
        res = self.request('variant', data={'id': 'chr8:g.7194707G>A'})
        assert '_license' in res.json()['exac_nontcga']

    def test_gnomad_exome(self):
        self._wait()
        res = self.request('variant', data={'id': 'chr8:g.7194707G>A'})
        assert '_license' in res.json()['gnomad_exome']

    def test_gnomad_genome(self):
        self._wait()
        res = self.request('variant', data={'id': 'chr8:g.7194707G>A'})
        assert '_license' in res.json()['gnomad_genome']


class TestBeaconEndpoints(BiothingsWebAppTest):
    pass
    # FIXME: document the endpoint and implement tests
    #  for /beacon/*, handlers in web.beacon.handlers


class TestGenomicIntervalQuery(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'mv_app_test'

    def test_standalone_interval_query_pos_hg19(self):
        self.query(data={'q': 'chr8:7194707'})

    def test_standalone_interval_query_range_hg19(self):
        self.query(data={'q': 'chr8:7194706-7194708'})

    def test_standalone_interval_query_pos_hg38(self):
        self.query(data={'q': 'chrX:30718532', 'assembly': 'hg38'})

    def test_prequery(self):
        self.query(data={'q': 'cadd.chrom:9 AND chr8:7194707'}, hits=False)
        self.query(data={'q': 'cadd.chrom:8 AND chr8:7194707'})

    def test_postquery(self):
        self.query(data={'q': 'chr8:7194707 AND cadd.chrom:9'}, hits=False)
        self.query(data={'q': 'chr8:7194707 cadd.chrom:9 OR cadd.chrom:8'})

    def test_pre_and_post_query(self):
        self.query(data={'q': 'dbnsfp.alt:A AND chr8:7194707 AND cadd.chrom:8'})
        self.query(data={'q': 'NOT dbnsfp.alt:A AND chr8:7194707 AND cadd.chrom:8'},
                   hits=False)
        self.query(data={'q': 'dbnsfp.alt:A AND chr8:7194707 AND NOT cadd.chrom:8'},
                   hits=False)

    def test_pre_and_post_query_logic(self):
        # we want something that messes up the old one when it
        # does the concatenation without () and breaking the
        # (intended) affinity
        # ES itself is very weird anyways,
        # see https://github.com/elastic/elasticsearch/issues/24847
        #
        # Explanation on the query used below
        # if it gets evaluated to
        #   (cadd.chrom:8 OR cadd.chrom:9) AND (cadd.chrom:8 OR cadd.chrom:9)
        # then there should be hits, but
        #   cadd.chrom:8 OR cadd.chrom:9 AND cadd.chrom:8 OR cadd.chrom:9
        # does not yield results. Despite the strange query, usually it makes
        # sense to add the parenthesis, and that's the better practices following
        # ES documentation anyways
        self.query(data={
            'q': 'cadd.chrom:8 OR cadd.chrom:9'
            'AND chr8:7194707 AND '
            'cadd.chrom:9 OR cadd.chrom:8'
        })


class TestIssue133(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'mv_app_test'

    def test_multiple_rsid(self):
        variants = ['rs771931171', 'rs1555101858', 'rs10474608', 'rs1047781'
                    'rs10479013', 'rs10479542', 'rs1048169', 'rs1048374']
        ids = ','.join([f'"{variant}"' for variant in variants])
        res = self.request('variant', method='POST',
                           data={'ids': ids}).json()
        for variant in variants:
            # we don't really care about the results
            assert self.value_in_result(variant, res, 'query')
        # this document is actually present, doesn't hurt to check
        assert self.value_in_result('rs771931171', res, 'dbsnp.rsid')
