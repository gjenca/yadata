import os,sys,errno,re
import yaml
import unicodedata
import tempfile
import shutil
from .record import Record,LogEntry
import warnings
try:
    import _yadata_types 
except ModuleNotFoundError:
    pass

class Datadir(list):

    def append(self,rec):

        list.append(self,rec)
        if "_key" in rec:
            self.keys[rec["_key"]]=rec

    def __init__(self,dirname):

        list.__init__(self)
        self.keys={}
        self.dirname=dirname
        if os.path.isdir(self.dirname):
            for root,dirs,files in os.walk(self.dirname):
                for name in files:
                    if name.endswith(".yaml"):
                        path=os.path.join(root,name)
                        with open(path) as f:
                            data=yaml.load(f,Loader=yaml.Loader)
                        if not issubclass(type(data),Record):
                            raise TypeError("File %s does not contain a Record subtype" % path)
                        data.path=path
                        self.append(data)
        else:
            raise NotADirectoryError("%s is not a directory" % dirname) 

    def list_matching(self,pattern):

        if "_key" in pattern and pattern["_key"] in self.keys:
            return [self.keys[pattern["_key"]]]
        else:
            return [rec for rec in self if type(rec)==type(pattern) and rec == pattern]
    
    def merge(self,object_to_merge,methods):

        matching_records=self.list_matching(object_to_merge)
        if not matching_records:
            object_to_merge.dirty=True
            object_to_merge.save(self)
            self.append(object_to_merge)
            return {},[LogEntry(object_to_merge['_key'],'new-record',None,None,None)]
        else:
            if len(matching_records)>1:
                matching_keys=[obj['_key'] for obj in matching_records]
                raise ValueError(f"""{len(matching_records)} matching records for {object_to_merge}
the keys are {matching_keys}""")
            else:
                matching_record=matching_records[0]
                bounce,log_record=matching_record.merge(object_to_merge,methods)
                matching_record.save(self)
                return bounce,log_record

