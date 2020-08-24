# -*- coding: utf-8 -*-
import os,sys,errno,re
import yaml
import unicodedata
import tempfile
import shutil
import warnings
import shelve

from .record import Record
try:
    import _yadata_types 
except ModuleNotFoundError:
    pass

from .indexed_dir import deepscan_dir

class Datadir(list):

    def append(self,rec):

        list.append(self,rec)
        if "_key" in rec:
            self.keys[rec["_key"]]=rec

    def __init__(self,dirname):

        list.__init__(self)
        self.keys={}
        self.dirname=dirname
        self.cache=shelve.open(os.path.join(dirname,'.cache.db'))
        deepscan_dir(dirname,self)
        for path,data in self.cache.items():
            data.path=path
            self.append(data)
        self.cache.close()

    def create(self,path):
        
        data=yaml.load(open(path),Loader=yaml.Loader)
        if not issubclass(type(data),Record):
            raise TypeError("File %s does not contain a Record subtype" % path)
        self.cache[path]=data

    def delete(self,path):

        del self.cache[path]

    def update(self,path):

        data=yaml.load(open(path),Loader=yaml.Loader)
        if not issubclass(type(data),Record):
            raise TypeError("File %s does not contain a Record subtype" % path)
        self.cache[path]=data

    def list_matching(self,pattern):

        if "_key" in pattern and pattern["_key"] in self.keys:
            return [self.keys[pattern["_key"]]]
        else:
            return [rec for rec in self if rec == pattern]
    
    def merge(self,object_to_merge,methods):

        matching_records=self.list_matching(object_to_merge)
        if not matching_records:
            object_to_merge.dirty=True
            object_to_merge.save(self)
            return {},[]
        else:
            if len(matching_records)>1:
                raise ValueError("%d matching records for %s" % (len(matching_records),object_to_merge))
            else:
                matching_record=matching_records[0]
                bounce,log_record=matching_record.merge(object_to_merge,methods)
                matching_record.save(self)
                return bounce,log_record

