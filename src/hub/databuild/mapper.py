import biothings.hub.databuild.mapper as mapper
from biothings import config as btconfig
logging = btconfig.logger
max_id_length = btconfig.MAX_ID_LENGTH

class TagObserved(mapper.BaseMapper):

    def load(self, *args, **kwargs):
        pass

    def process(self,docs):
        for doc in docs:
            doc.update({'observed':True})
            yield doc

class SkipLongId(mapper.BaseMapper):

    def load(self, *args, **kwargs):
        pass

    def process(self,docs):
        for doc in docs:
            if len(doc["_id"]) > max_id_length:
                logging.debug("Skip doc, _id too long: %s" % doc["_id"])
                continue
            yield doc
    
class TagObservedAndSkipLongId(TagObserved,SkipLongId):
    
    def process(self,docs):
        okdocs = SkipLongId.process(self,docs)
        obsdocs = TagObserved.process(self,okdocs)
        return obsdocs
