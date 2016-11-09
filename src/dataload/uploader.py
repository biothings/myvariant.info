import biothings.dataload.uploader as uploader

class SnepffPostUpdateUploader(uploader.BaseSourceUploader):

    def post_update_data(self):
        self.logger.info("Updating snpeff information from source '%s' (collection:%s)" % (self.fullname,self.collection_name))
