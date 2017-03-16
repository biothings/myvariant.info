import re, os, sys, pickle, datetime
import subprocess

from biothings.utils.dataload import unlist, dict_sweep
from utils.validate import bit_to_nuc
from biothings.utils.common import loadobj
from utils.hgvs import get_hgvs_from_vcf, trim_delseq_from_hgvs

from biothings import config
logger = config.logger


class VCFConstruct(object):

    def __init__(self, genome):
        self.genome = genome
        self._chr_data = None

    def load_chr_data(self):
        logger.info("\tLoading chromosome data from '%s'..." % self.genome)
        try:
            self._chr_data = loadobj(self.genome)
        except Exception as e:
            logger.info(e)
            raise
        logger.info("Done.")

    def snp_hgvs_id_parser(self, id):
        '''get chr, pos, ref, alt from hgvs_id'''
        pat = 'chr(\w+):g\.(\d+)(\w)\>(\w)'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def del_hgvs_id_parser_interval(self, id):
        pat = 'chr(\w+):g\.(\d+)\_(\d+)del'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def del_hgvs_id_parser(self, id):
        pat = 'chr(\w+):g\.(\d+)del'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def ins_hgvs_id_parser(self, id):
        pat = 'chr(\w+):g\.(\d+)\_(\d+)ins(\w+)'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def delins_hgvs_id_parser(self, id):
        pat = 'chr(\w+):g\.(\d+)\_(\d+)delins(\w+)'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def snp_vcf_constructor(self, hgvs):
        '''construct a VCF file based on chr, pos, ref, alt information'''
        chrom = hgvs[0]
        if chrom == 'MT':
            chrom = 'M'
        pos = hgvs[1]
        ref = hgvs[2]
        alt = hgvs[3]
        vcf = {"chrom": str(chrom), "position": str(pos), "ref": ref, "alt": alt}
        return vcf

    def del_vcf_constructor(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1]) - 1
        # len=2 was a single del, len=3 was internval del
        if len(hgvs) == 2:
            end = int(hgvs[1])
        else:
            end = int(hgvs[2])
        chr_bit = self._chr_data[str(chrom)]
        ref = ''
        for i in range(pos, end+1):
            try:
                nuc_chr_bit = chr_bit[i*4-4:i*4]
                nuc_chr = bit_to_nuc(nuc_chr_bit)
                ref += nuc_chr
            except Exception as e:
                logger.warning("Couldn't extract nucleotide from bits with HGVS %s: %s" % (repr(hgvs),e))
                return None
        alt = ref[0]
        if chrom == 'MT':
            chrom = 'M'
        vcf = {"chrom": str(chrom), "position": str(pos), "ref": ref, "alt": alt}
        return vcf

    def ins_vcf_constructor(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1])
        chr_bit = self._chr_data[str(chrom)]
        nuc_chr_bit = chr_bit[pos*4-4:pos*4]
        try:
            ref = bit_to_nuc(nuc_chr_bit)
        except Exception as e:
            logger.warning("Couldn't extract nucleotide from bits with HGVS %s: %s" % (repr(hgvs),e))
            return None
        alt = hgvs[3]
        alt = ref + alt
        if chrom == 'MT':
            chrom = 'M'
        vcf = {"chrom": str(chrom), "position": str(pos), "ref": ref, "alt": alt}
        return vcf

    def delins_vcf_constructor(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1])
        end = int(hgvs[2])
        chr_bit = self._chr_data[str(chrom)]
        ref = ''
        for i in range(pos, end+1):
            try:
                nuc_chr_bit = chr_bit[i*4-4:i*4]
                nuc_chr = bit_to_nuc(nuc_chr_bit)
                ref += nuc_chr
            except Exception as e:
                logger.warning("Couldn't extract nucleotide from bits with HGVS %s: %s" % (repr(hgvs),e))
                return None
        alt = hgvs[3]
        if chrom == 'MT':
            chrom = 'M'
        vcf = {"chrom": str(chrom), "position": str(pos), "ref": ref, "alt": alt}
        return vcf

    def build_vcfs(self, hgvs_ids):
        '''load data'''
        # extract each hgvs_id from list, transform into vcf format
        hgvs_vcfs = {}
        for hgvs_id in hgvs_ids:
            if '>' in hgvs_id:
                hgvs_info = self.snp_hgvs_id_parser(hgvs_id)
                if not hgvs_info:
                    continue
                vcf = self.snp_vcf_constructor(hgvs_info)
                if not vcf:
                    continue
                hgvs_vcfs[hgvs_id] = {"_id" : hgvs_id, "vcf" : vcf}

            elif hgvs_id.endswith('del') and '_' in hgvs_id:
                hgvs_info = self.del_hgvs_id_parser_interval(hgvs_id)
                if not hgvs_info:
                    continue
                vcf = self.del_vcf_constructor(hgvs_info)
                if not vcf:
                    continue
                hgvs_vcfs[hgvs_id] = {"_id" : hgvs_id, "vcf" : vcf}

            elif hgvs_id.endswith('del') and '_' not in hgvs_id:
                hgvs_info = self.del_hgvs_id_parser(hgvs_id)
                if not hgvs_info:
                    continue
                vcf = self.del_vcf_constructor(hgvs_info)
                if not vcf:
                    continue
                hgvs_vcfs[hgvs_id] = {"_id" : hgvs_id, "vcf" : vcf}

            elif 'ins' in hgvs_id and 'del' not in hgvs_id:
                hgvs_info = self.ins_hgvs_id_parser(hgvs_id)
                if not hgvs_info:
                    continue
                vcf = self.ins_vcf_constructor(hgvs_info)
                if not vcf:
                    continue
                hgvs_vcfs[hgvs_id] = {"_id" : hgvs_id, "vcf" : vcf}

            elif 'delins' in hgvs_id:
                hgvs_info = self.delins_hgvs_id_parser(hgvs_id)
                if not hgvs_info:
                    continue
                vcf = self.delins_vcf_constructor(hgvs_info)
                if not vcf:
                    continue
                hgvs_vcfs[hgvs_id] = {"_id" : hgvs_id, "vcf" : vcf}

            else:
                logger.info('%s: beyond current capacity, skip it' % hgvs_id)
                continue

        return hgvs_vcfs


class SnpeffAnnotator(object):

    def __init__(self,cmd):
        if type(cmd) == str:
            self.snpeff_cmd = cmd.split()
        else:
            self.snpeff_cmd = cmd

    def check_hgvs_info(self,hgvs_info):
        # last one should be a nucleotide
        if not re.match("[ATGC]",hgvs_info["alt"]):
            raise ValueError("Invalid nucleotide in HGVS info: %s" % repr(hgvs_info))
        if not hgvs_info["chrom"] in [str(i) for i in range(1,23)] + ["X","Y","M"]:
            raise ValueError("Invalid chromosome in HGVS info: %s" % repr(hgvs_info))

    def annotate(self,hgvs_vcfs):
        """hgvs_vcfs: list of {"vcf": {}, "_id": ""}"""

        # title of vcf
        vcf_stdin = ['#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO']
        logger.info("Running '%s'" % self.snpeff_cmd)
        for hgvs_id in hgvs_vcfs:
            vcf = hgvs_vcfs[hgvs_id]["vcf"]
            try:
                self.check_hgvs_info(vcf)
            except (TypeError, ValueError) as e:
                logger.warning("Skipping HGVS %s: %s" % (repr(hgvs_vcfs[hgvs_id]),e))
                continue
            # add hgvs ID at the end so we can match for sure which annotations correspond to which ID 
            # instead of rebuild it from VCF info (they can be different)
            # this comment will be at the first position in the result line
            vcf_stdin.append(str(vcf["chrom"]) + '\t' + str(vcf["position"]) + '\t' + '.' + '\t' + vcf["ref"] + '\t' + vcf["alt"] + '\t.\t.\t.' + "\t# hgvs:" + hgvs_id)

        proc = subprocess.Popen(self.snpeff_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate("\n".join(vcf_stdin).encode())
        if stderr.decode() != '':
            fn = "snpeff_err_%s.pickle" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            pickle.dump({"input" : hgvs_vcfs,
                         "vcf_stdin" : vcf_stdin,
                         "stderr" : stderr.decode()},open(fn,"wb"))
            raise Exception("Something went wrong while generating snpeff annotation (see dump %s for more):\n%s" % (fn,stderr.decode()))

        strout = stdout.decode()
        vcf_stdout_raw = strout.splitlines()
        for vcf_line in vcf_stdout_raw:
            if vcf_line.startswith('#'):
                continue
            elif vcf_line == '':
                continue
            else:
                fromi = vcf_line.index("#")
                str_id = vcf_line[fromi:]
                hgvs_info = str_id.replace("#","").strip().split(":")
                # extract HGVS
                assert hgvs_info[0] == "hgvs", "Can't find HGVS ID in VCF line '%s'" % repr(vcf_line)
                hgvs_id = ":".join(hgvs_info[1:])
                # -1: remove the tab char also, before #
                vcf_line = vcf_line[:fromi-1]
                # assume the following item is 'ANN'
                ann_info = vcf_line.split(';')[0]
                ann = []
                # Multiple annotations per VCF line
                for item in ann_info.split(','):
                    if len(item.split('|')) > 1:
                        (effect, putative_impact, gene_name, gene_id, feature_type, feature_id) = item.split('|')[1:7]
                        (transcript_biotype, exon, hgvs_coding, hgvs_protein, cdna, cds, protein, distance_to_feature) = item.split('|')[7:15]
                        if cdna:
                            (cdna_position, cdna_len) = cdna.split('/')
                        else:
                            cdna_position = None
                            cdna_len = None
                        if cds:
                            (cds_position, cds_len) = cds.split('/')
                        else:
                            cds_position = None
                            cds_len = None
                        if protein:
                            (protein_position, protein_len) = protein.split('/')
                        else:
                            protein_position = None
                            protein_len = None
                        if exon:
                            (rank, total) = exon.split('/')
                        else:
                            rank = None
                            total = None
                        ann.append({
                            "effect": effect,
                            "putative_impact": putative_impact,
                            "genename": gene_name,
                            "gene_id": gene_id,
                            "feature_type": feature_type,
                            "feature_id": feature_id,
                            "transcript_biotype": transcript_biotype,
                            "rank": rank,
                            "total": total,
                            "hgvs_c": trim_delseq_from_hgvs(hgvs_coding), # trim long sequence
                            "hgvs_p": hgvs_protein,
                            "cdna": {
                                "position": cdna_position,
                                "length": cdna_len
                            },
                            "cds": {
                                "position": cds_position,
                                "length": cds_len
                            },
                            "protein": {
                                "position": protein_position,
                                "length": protein_len
                            },
                            "distance_to_feature": distance_to_feature
                        })
                # not all annotations include lof & nmd information. Set them to 'None' as default
                lof = None
                nmd = None
                # the case that annotation include 'ann' & 'lof' & 'nmd'
                if len(vcf_line.split(';')) == 3:
                    (lof_info, nmd_info) = vcf_line.split(';')[1:3]
                    # assume the second item is 'lof'
                    assert lof_info.startswith('LOF')
                    # the information to be parsed is like this: 'LOF=(PTEN|PTEN|1|1.00)'
                    lof_info = lof_info.split('(')[1].split(')')[0]
                    nmd_info = nmd_info.split('(')[1].split(')')[0]
                    (id_lof, name_lof, nt_lof, pt_lof) = lof_info.split('|')
                    (id_nmd, name_nmd, nt_nmd, pt_nmd) = nmd_info.split('|')
                    lof = {
                        "gene_id": id_lof,
                        "genename": name_lof,
                        "number_of_transcripts_in_gene": nt_lof,
                        "percent_of_transcripts_affected": pt_lof
                    }
                    nmd = {
                        "gene_id": id_nmd,
                        "genename": name_nmd,
                        "number_of_transcripts_in_gene": nt_nmd,
                        "percent_of_transcripts_affected": pt_nmd
                    }
                # the case that annotation include 'ann' & 'lof or nmd'
                elif len(vcf_line.split(';')) == 2:
                    (ann_info, idk_info) = vcf_line.split(';')
                    if idk_info.startswith('LOF'):
                        lof_info = idk_info.split('(')[1].split(')')[0]
                        (id_lof, name_lof, nt_lof, pt_lof) = lof_info.split('|')
                        lof = {
                            "gene_id": id_lof,
                            "genename": name_lof,
                            "number_of_transcripts_in_gene": nt_lof,
                            "percent_of_transcripts_affected": pt_lof
                        }
                    else:
                        nmd_info = idk_info.split('(')[1].split(')')[0]
                        (id_nmd, name_nmd, nt_nmd, pt_nmd) = nmd_info.split('|')
                        nmd = {
                            "gene_id": id_nmd,
                            "genename": name_nmd,
                            "number_of_transcripts_in_gene": nt_nmd,
                            "percent_of_transcripts_affected": pt_nmd
                        }
                (chrom, pos, _id, ref, alt) = ann_info.split('\t')[0:5]
                one_snp_json = {
                    "_id": hgvs_id,
                    "snpeff": {
                        "ann": ann,
                        "lof": lof,
                        "nmd": nmd,
                    },
                }
                snpeff_json = dict_sweep(unlist(one_snp_json), vals=['', None])

                yield snpeff_json
