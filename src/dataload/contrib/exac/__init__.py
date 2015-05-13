def get_mapping():
	mapping = {
		"exac": {
			"properties": {
				"chrom": {
					"type": "string",
					"analyzer": "string_lowercase"
				}
			}
		}
	}