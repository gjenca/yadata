
import shutil
import os
import errno
import tempfile
import yadata.sane_yaml as sane_yaml

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class Record(dict):
    """ Base class for all types of records.
"""

    def __init__(self,d,path=None,datadir=None):
        self.path=path
        self.datadir=datadir
        self.dirty=False
        dict.__init__(self,d)

    def __setitem__(self,key,value):
        self.dirty=True
        dict.__setitem__(self,key,value)

    def generate_keys(self):

        prefix=self.get_key_prefix()
        yield prefix
        i=0
        while True:
           yield f"{prefix}_{i}"
           i+=1

    def save(self):
        if not self.dirty:
            return
        
        if not "key" in self:
            for key in self.generate_keys():
                if key not in self.datadir.keys:
                    self["key"]=key
                    break
        
        if self.path is None:
            if self.datadir is None:
                raise SaveError("Cannot save: no path and no datadir given") 
            pathdir=os.path.join(self.datadir.dirname,self.get_subdir())
            mkdir_p(pathdir)
            self.path=os.path.join(pathdir,("%s.yaml" % self["key"]))
        f=tempfile.NamedTemporaryFile(delete=False,mode='w')
        f.write(sane_yaml.dump(dict(self)))
        f.close()
        print(f.name,'->',self.path)
        shutil.move(f.name,self.path)


yaml=ruamel.yaml.YAML()


