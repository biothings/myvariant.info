# -*- coding: utf-8 -*-
import pandas as pd


def rs2hgvs(mv, rs_id):
    var = mv.queryvariant(rs_id)
    hgvs = [(rs_id, variant['_id']) for variant in var['hits'] if variant]
    return hgvs


def write_file(url):
    pages = range(1, 5)
    urls = map(lambda x: url + str(x), pages)
    drugbank_df = pd.concat(map(lambda url: pd.read_html(url)[0], urls))

    rs_ids = drugbank_df['SNP RS ID']
    mv = MyVariantInfo()
    hgvs = [rs2hgvs(mv, rs_id) for rs_id in rs_ids]
    id_df = pd.concat(map(pd.DataFrame, hgvs))

    id_df.columns = "rs_id", "hgvs_id"
    drugbank_df.rename(columns={"SNP RS ID": "rs_id"}, inplace=True)

    drugbank_df.set_index("rs_id", inplace=True)
    id_df.set_index("rs_id", inplace=True)
    df = id_df.join(drugbank_df, how='right').drop_duplicates()
    df.sort(columns='hgvs_id', inplace=True)
    df.to_csv('/opt/myvariant.info/load_archive/drugbank/drugbank.csv')
    return df
