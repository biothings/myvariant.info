from __future__ import print_function

import re
import subprocess

from utils.dataload import unlist, dict_sweep

SNPEFF_CMD = 'java -Xmx4g -jar /home/kevinxin/snpEff/snpEff.jar hg19'.split()


def hgvs_id_parser(id):
    '''get chr, pos, ref, alt from hgvs_id'''
    pat = 'chr(\w+):g\.(\d+)(\w)\>(\w)'
    mat = re.match(pat, id)
    if mat:
        r = mat.groups()
        return r


def vcf_constructer(hgvs):
    '''construct a VCF file based on chr, pos, ref, alt information'''
    chrom = hgvs[0]
    pos = hgvs[1]
    ref = hgvs[2]
    alt = hgvs[3]
    vcf = str(chrom) + '\t' + str(pos) + '\t' + '.' + '\t' + ref + '\t' + alt + '\t.\t.\t.\n'
    return vcf


def hgvs_id_constructer(vcf_line):
    '''construct a hgvs id based on vcf_line information'''
    (chr, pos, _id, ref, alt) = vcf_line.split('\t')[0:5]
    hgvs_id = 'chr' + chr + ':g.' + pos + ref + '>' + alt
    return hgvs_id


def annotate_by_snpeff(varobj_list):
    '''load data'''
    # title of vcf
    vcf_stdin = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n'
    # extract each item from list, transform into vcf format
    snpeff_valid_id = []
    for item in varobj_list:
        hgvs_info = hgvs_id_parser(item)
        try:
            vcf_stdin += vcf_constructer(hgvs_info)
        except TypeError:
            print(item)
            continue
        snpeff_valid_id.append(item)

    proc = subprocess.Popen(SNPEFF_CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate(vcf_stdin)
    assert stderr == '', stderr

    snpeff_json_list = []
    vcf_stdout_raw = stdout.split('\n')
    i = 0
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
                (effect, putative_impact, gene_name, gene_id, feature_type, feature_id) = item.split('|')[1:7]
                (transcript_biotype, exon, hgvs_coding, hgvs_protein, cdna, cds, protein, distance_to_feature) = item.split('|')[7:15]
                try:
                    (cdna_position, cdna_len) = cdna.split('/')
                except ValueError:
                    cdna_position = None
                    cdna_len = None
                    continue
                (cds_position, cds_len) = cds.split('/')
                (protein_position, protein_len) = protein.split('/')
                (rank, total) = exon.split('/')
                ann.append({
                    "effect": effect,
                    "putative_impact": putative_impact,
                    "gene_name": gene_name,
                    "gene_id": gene_id,
                    "feature_type": feature_type,
                    "feature_id": feature_id,
                    "transcript_biotype": transcript_biotype,
                    "rank": rank,
                    "total": total,
                    "hgvs.c": hgvs_coding,
                    "hgvs.p": hgvs_protein,
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
                    "gene_name": name_lof,
                    "number_of_transcripts_in_gene": nt_lof,
                    "percent_of_transcripts_affected": pt_lof
                }
                nmd = {
                    "gene_id": id_nmd,
                    "gene_name": name_nmd,
                    "number_of_transcripts_in_gene": nt_nmd,
                    "percent_of_transcripts_affected": pt_nmd
                }
            # the case that annotation include 'ann' & 'lof or nmd'
            elif len(vcf_line.split(';')) == 2:
                (ann_info, idk_info) = vcf_line.split(';')
                if idk_info.startswith('LOF'):
                    lof_info = lof_info.split('(')[1].split(')')[0]
                    (id_lof, name_lof, nt_lof, pt_lof) = lof_info.split('|')
                    lof = {
                        "gene_id": id_lof,
                        "gene_name": name_lof,
                        "number_of_transcripts_in_gene": nt_lof,
                        "percent_of_transcripts_affected": pt_lof
                    }
                else:
                    nmd_info = nmd_info.split('(')[1].split(')')[0]
                    (id_nmd, name_nmd, nt_nmd, pt_nmd) = nmd_info.split('|')
                    nmd = {
                        "gene_id": id_nmd,
                        "gene_name": name_nmd,
                        "number_of_transcripts_in_gene": nt_nmd,
                        "percent_of_transcripts_affected": pt_nmd
                    }
            one_snp_json = {
                "id": hgvs_id_constructer(vcf_line),
                "snpeff": {
                    "ann": ann,
                    "lof": lof,
                    "nmd": nmd
                }
            }
            snpeff_json = dict_sweep(unlist(one_snp_json), vals=['', None])
            snpeff_json_list.append(snpeff_json)
            i += 1
            print(i)
    return snpeff_json_list
