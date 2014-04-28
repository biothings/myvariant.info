#!/usr/bin/python

import mwparserfromhell
import re
import json
from wikitools import wiki
from wikitools import page
from wikitools import category

site = wiki.Wiki("http://bots.snpedia.com/api.php")
snp = "Rs7495174"

snps = category.Category(site, "Is_a_snp")
snpedia = []
dict = {}  
       
# pagehandle = page.Page(site,snp)
# snp_page = pagehandle.getWikiText()
# wikicode = mwparserfromhell.parse(snp_page)
# templates=wikicode.filter_templates()
# template = templates[0] 
# chr = template.get("Chromosome").value.decode("iso-8859-1").rstrip()
# pos = template.get("position").value.decode("iso-8859-1").rstrip()
# mut = template.get("geno2").value.decode("iso-8859-1").rstrip()
# match = re.search(r'\((\w);(\w)\)', mut)
# hgvs = chr +":g."+pos+match.group(1)+">"+match.group(2)
# # for template in templates:
# # 	print template
# # 	#print "\n\n"
# text = wikicode.strip_code()
# dict[hgvs] = {"_id" : hgvs, "text" : text}

# {{Rsnum
# |rsid=7495174
# |Gene=OCA2
# |Chromosome=15
# |position=28344238
# |Orientation=plus
# |GMAF=0.2585
# |Assembly=GRCh37
# |GenomeBuild=37.1
# |dbSNPBuild=131
# |geno1=(A;A)
# |geno2=(A;G)
# |geno3=(G;G)
# }}

# print text


for article in snps.getAllMembersGen(namespaces=[0]):   # get all snp-names as list and print them
	print article
	snpedia.append(article.title.lower())
	pagehandle = page.Page(site,article.title)
	snp_page = pagehandle.getWikiText()
	wikicode = mwparserfromhell.parse(snp_page)
	templates=wikicode.filter_templates()
	template = templates[0]
	print template.name
	#print snp_page
	if not "23andMe" in template.name:
		if not "OMIM SNP" in template.name:
			print template
			try:
				chr = template.get("Chromosome").value.decode("iso-8859-1").rstrip()
				pos = template.get("position").value.decode("iso-8859-1").rstrip()
				mut = template.get("geno2").value.decode("iso-8859-1").rstrip()	
				match = re.search(r'\((\w+|-);(\w+|-)\)', mut)
				hgvs = chr +":g."+pos+match.group(1)+">"+match.group(2)
				text = wikicode.strip_code()
				print hgvs
				print text
				if text:
					dict[hgvs] = {"_id" : hgvs, "text" : text}
			except (ValueError, AttributeError, UnicodeEncodeError) as e:
				print "Value not found on page"	
				
print json.dumps(dict)