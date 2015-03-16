import importlib

sources = ['cadd', 'clinvar', 'cosmic2', 'dbnsfp', 'dbsnp', 'drugbank', 'emv', 'evs', 'grasp']


m = {
	"variant": {
		"include_in_all": False,
		"dynamic": False,
		"properties": {}
	}
}



for src in sources:
	print src
	src_m = importlib.import_module('dataload.contrib.' + src + '.__init__')
	print src_m
	_m = src_m.get_mapping()
	print _m
	m['variant']['properties'].update(_m)

	print m

	return m