import re, os, sys
import subprocess

from biothings.utils.dataload import unlist, dict_sweep
from utils.validate import bit_to_nuc
from biothings.utils.common import loadobj
from utils.hgvs import get_hgvs_from_vcf

import logging
logger = logging.getLogger("snpeff")


class VCFConstruct:
    def __init__(self,cmd, genome):
        if type(cmd) == str:
            self.snpeff_cmd = cmd.split()
        else:
            self.snpeff_cmd = cmd
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

    def del_hgvs_id_parser(self, id):
        pat = 'chr(\w+):g\.(\d+)\_(\d+)del'
        mat = re.match(pat, id)
        if mat:
            r = mat.groups()
            return r

    def del_hgvs_id_parser1(self, id):
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

    def snp_vcf_constructer(self, hgvs):
        '''construct a VCF file based on chr, pos, ref, alt information'''
        chrom = hgvs[0]
        if chrom == 'MT':
            chrom = 'M'
        pos = hgvs[1]
        ref = hgvs[2]
        alt = hgvs[3]
        vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
        return vcf

    def del_vcf_constructor(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1]) - 1
        end = int(hgvs[2])
        chr_bit = self._chr_data[str(chrom)]
        ref = ''
        for i in range(pos, end+1):
            nuc_chr_bit = chr_bit[i*4-4:i*4]
            nuc_chr = bit_to_nuc(nuc_chr_bit)
            ref += nuc_chr
        alt = ref[0]
        if chrom == 'MT':
            chrom = 'M'
        vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
        return vcf

    def del_vcf_constructor1(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1]) - 1
        end = int(hgvs[1])
        chr_bit = self._chr_data[str(chrom)]
        ref = ''
        for i in range(pos, end+1):
            nuc_chr_bit = chr_bit[i*4-4:i*4]
            nuc_chr = bit_to_nuc(nuc_chr_bit)
            ref += nuc_chr
        alt = ref[0]
        vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
        return vcf

    def ins_vcf_constructor(self, hgvs):
        if self._chr_data is None:
            self.load_chr_data()
        chrom = hgvs[0]
        pos = int(hgvs[1])
        chr_bit = self._chr_data[str(chrom)]
        nuc_chr_bit = chr_bit[pos*4-4:pos*4]
        ref = bit_to_nuc(nuc_chr_bit)
        alt = hgvs[3]
        alt = ref + alt
        if chrom == 'MT':
            chrom = 'M'
        vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
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
            nuc_chr_bit = chr_bit[i*4-4:i*4]
            nuc_chr = bit_to_nuc(nuc_chr_bit)
            ref += nuc_chr
        alt = hgvs[3]
        if chrom == 'MT':
            chrom = 'M'
        vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
        return vcf

    def annotate_by_snpeff(self, varobj_list):
        '''load data'''
        # title of vcf
        vcf_stdin = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n'
        # extract each item from list, transform into vcf format
        snpeff_valid_id = []
        for item in varobj_list:
            # annotations are 3kb on average, when we have N nucleotide, we have to limit
            # the number of generated annotations, otherwise we can't store them
            # (document is too big). 3KB * 4**5 = 3MB, we're on the safe side
            if item.count("N") > 5:
                logger.warning("Can't process '%s', it would produce a document too big" % item)
                continue
            if '>' in item:
                hgvs_info = self.snp_hgvs_id_parser(item)
                try:
                    vcf_stdin += self.snp_vcf_constructer(hgvs_info)
                except (TypeError, ValueError):
                    #logger.info(item)
                    continue
                snpeff_valid_id.append(item)
            elif item.endswith('del') and '_' in item:
                hgvs_info = self.del_hgvs_id_parser(item)
                try:
                    vcf_stdin += self.del_vcf_constructor(hgvs_info)
                except (TypeError, ValueError):
                    #logger.info(item)
                    continue
                snpeff_valid_id.append(item)
            elif item.endswith('del') and '_' not in item:
                hgvs_info = self.del_hgvs_id_parser1(item)
                try:
                    vcf_stdin += self.del_vcf_constructor1(hgvs_info)
                except (TypeError, ValueError):
                    #logger.info(item)
                    continue
                snpeff_valid_id.append(item)
            elif 'ins' in item and 'del' not in item:
                hgvs_info = self.ins_hgvs_id_parser(item)
                try:
                    vcf_stdin += self.ins_vcf_constructor(hgvs_info)
                except (TypeError, ValueError):
                    #logger.info(item)
                    continue
                snpeff_valid_id.append(item)
            elif 'delins' in item:
                hgvs_info = self.delins_hgvs_id_parser(item)
                try:
                    vcf_stdin += self.delins_vcf_constructor(hgvs_info)
                except (TypeError, ValueError):
                    #logger.info(item)
                    continue
                snpeff_valid_id.append(item)
            else:
                logger.info(item)
                logger.info('beyond current capacity')
        proc = subprocess.Popen(self.snpeff_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate(vcf_stdin.encode())
        it = iter(snpeff_valid_id)
        if stderr.decode() != '':
            raise Exception("Something went wrong while generating snpeff annotation:\n%s" % stderr)

        strout = stdout.decode()
        vcf_stdout_raw = strout.split('\n')
        for vcf_line in vcf_stdout_raw:
            if vcf_line.startswith('#'):
                continue
            elif vcf_line == '':
                continue
            else:
                # assume the first item is 'ANN'
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
                            "hgvs_c": hgvs_coding,
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
                if chrom == 'M':
                    chrom = 'MT'
                try:
                    hgvs_id = get_hgvs_from_vcf(chrom, pos, ref, alt)
                except Exception as e:
                    logger.info(e)
                    next(it)
                    continue
                one_snp_json = {
                    "_id": hgvs_id,
                    "snpeff": {
                        "ann": ann,
                        "lof": lof,
                        "nmd": nmd,
                    },
                    "vcf": {
                        "position": pos,
                        "ref": ref,
                        "alt": alt
                    }
                }
                snpeff_json = dict_sweep(unlist(one_snp_json), vals=['', None])
                orig_id = next(it)
                if orig_id != snpeff_json["_id"]:
                    logger.info("Skip, hgvs IDs are different: '%s' != '%s'" % (orig_id,snpeff_json["_id"]))
                    continue

                yield snpeff_json
