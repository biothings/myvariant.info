
# coding: utf-8

# In[8]:

from bitarray import bitarray
import re
import os
import types

# encode nucleotide into bit form
def nuc_to_bit(sequence):
    code = {'A':bitarray('001'),'C':bitarray('010'),
                       'G':bitarray('011'),'T':bitarray('100'),
                       'g':bitarray('011'),'t':bitarray('100'),
                       'a':bitarray('001'),'c':bitarray('010'),
                       'N':bitarray('101'),'M':bitarray('110'),
                       'R':bitarray('111')}
    seq_bit = bitarray()
    seq_bit.encode(code,sequence)
    return(seq_bit)

# load compressed chromsome fasta_to_bit file
def loadobj(filename, mode='file'):
    '''Loads a compressed object from disk file (or file-like handler) or
        MongoDB gridfs file (mode='gridfs')
           obj = loadobj('data.pyobj')

           obj = loadobj(('data.pyobj', mongo_db), mode='gridfs')
    '''
    import gzip
    import cPickle as pickle

    if mode == 'gridfs':
        import gridfs
        filename, db = filename   # input is a tuple of (filename, mongo_db)
        fs = gridfs.GridFS(db)
        fobj = fs.get(filename)
    else:
        if type(filename) in types.StringTypes:
            fobj = file(filename, 'rb')
        else:
            fobj = filename   # input is a file-like handler
    gzfobj = gzip.GzipFile(fileobj=fobj)
    try:
        buffer = ""
        while 1:
            data = gzfobj.read()
            if data == "":
                break
            buffer += data
        object = pickle.loads(buffer)
    finally:
        gzfobj.close()
        fobj.close()
    return object

#parse variant name, print the variant name and return chromosome number, nucleotide position and nucleotide name
def parse(str):
    pat = 'chr(\w+):g\.(\d+)(\w)\>(\w)'
    mat = re.match(pat,str)
    print str
    if mat:
        r = mat.groups()
        return (r[0],r[1],r[2])

        
    
    
class VariantValidator:
    def __init__(self):
        self.data = 'NULL'
    
    #validate single hgvs variant name
    def validate_hgvs(self,hgvs_id):
        r = parse (hgvs_id)
        if r:
            #get the chromosome sequence in bit form
            if self.data == 'NULL':
                global chr_dict1 
                chr_dict1= loadobj('chr_dict.pyobj') 
                self.data = 1
            chr_bit = bitarray()
            if r[0]=='M':
                chr='MT'
            else:
                chr=r[0]
            chr_bit = chr_dict1[str(chr)]
            #get the nucleotide in chromsome sequence in bit form
            nuc_chr_bit = bitarray()
            nuc_chr_bit = chr_bit[int(r[1])*3-3:int(r[1])*3]
            #encode mutant nucleotide into bit form
            mut_bit = bitarray()
            mut_bit = nuc_to_bit (r[2])
            if (nuc_chr_bit == mut_bit ):
                print 'TRUE\n'
            else:
                print 'FALSE\n'
        else:
            print 'NULL\n'
            
    
    #validate multiple hgvs variant name
    def validate_many(self,*id_list):
        for item in id_list:
            self.validate_hgvs(item)


# In[ ]:



