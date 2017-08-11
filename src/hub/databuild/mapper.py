from biothings.utils.common import loadobj
import biothings.hub.databuild.mapper as mapper

class TagObserved(mapper.BaseMapper):

    def load(self, *args, **kwargs):
        pass

    def process(self,docs):
        for doc in docs:
            doc.update({'observed':True})
            yield doc

