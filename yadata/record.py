
import shutil
import os
import errno
import tempfile
import yadata.sane_yaml as sane_yaml
import yaml

def YadataRecord(cls):

    def cls_representer(dumper,data):

        return dumper.represent_mapping(cls.yadata_tag,dict(data),flow_style=False)

    def cls_constructor(loader,node):

        dict_value=loader.construct_mapping(node)
        return cls(dict_value)

    yaml.add_representer(cls,cls_representer)
    yaml.add_constructor(cls.yadata_tag,cls_constructor)

    return cls

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise

class Record(dict):
    """ Base class for all types of records.
"""

    def __init__(self,d):
        self.path=None
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

    def save(self,datadir):

        if not self.dirty:
            return
        
        if not "key" in self:
            for key in self.generate_keys():
                if key not in datadir.keys:
                    self["key"]=key
                    break
        
        if self.path is None:
            pathdir=os.path.join(datadir.dirname,self.subdir)
            mkdir_p(pathdir)
            self.path=os.path.join(pathdir,("%s.yaml" % self["key"]))
        f=tempfile.NamedTemporaryFile(delete=False,mode='w')
        f.write(sane_yaml.dump(self))
        f.close()
        shutil.move(f.name,self.path)

    
    def method_SET(self,field,value):

        self[field]=value

    def method_UNION(self,field,value):

        self[field]=list(set(self[field]+value))

    def method_EXTEND(self,field,value):

        self[field].extend(value)

    def method_DELETE(self,field,value=None):

        del self[field]
   
    method_dispatcher={
        "set":method_SET,
        "union":method_UNION,
        "extend":method_EXTEND,
        "delete":method_DELETE,
    }


    def merge(self,other,methods):
       
        if "key" not in self:
            raise ValueError("Attempted to merge with a record without key")
        bounced={}
        for field in other:
            if field not in self:
                self[field]=other[field]
            elif self[field]!=other[field]:
                if field not in methods:
                    bounced[field]=other[field]
                else:
                    self.method_dispatcher[methods[field]](self,field,other[field])
        return bounced
