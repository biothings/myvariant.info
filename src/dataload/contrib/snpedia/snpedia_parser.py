#!/usr/bin/python

import mwparserfromhell
import re
import json
from wikitools import wiki
from wikitools import page
from wikitools import category

site = wiki.Wiki("http://bots.snpedia.com/api.php")
snps = category.Category(site, "Is_a_snp")
snpedia = []
dict = {}

for article in snps.getAllMembersGen(namespaces=[0]):   # get all snp-names as list and print them
    snpedia.append(article.title.lower())
    pagehandle = page.Page(site, article.title)
    snp_page = pagehandle.getWikiText()
    wikicode = mwparserfromhell.parse(snp_page)
    templates = wikicode.filter_templates()
    template = templates[0]
    # print snp_page
    if not "23andMe" in template.name:
        if not "OMIM SNP" in template.name:
            try:
                chr = template.get("Chromosome").value.decode("iso-8859-1").rstrip()
                pos = template.get("position").value.decode("iso-8859-1").rstrip()
                mut = template.get("geno2").value.decode("iso-8859-1").rstrip()
                match = re.search(r'\((\w+|-);(\w+|-)\)', mut)
                hgvs = chr + ":g." + pos + match.group(1) + ">" + match.group(2)
                text = wikicode.strip_code()
                if text:
                    dict[hgvs] = {"_id": hgvs, "text": text}
            except (ValueError, AttributeError, UnicodeEncodeError) as e:
                error = "Value not found on page"
print json.dumps(dict)
