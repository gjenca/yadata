# -*- coding: utf-8 -*-
import os,sys,errno,re
import yaml
import unicodedata
import tempfile
import shutil
from .record import Record
import _yadata_types 

class Datadir(list):

    def append(self,rec):

        list.append(self,rec)
        if "_key" in rec:
            self.keys[rec["_key"]]=rec

    def __init__(self,modulename):

        list.__init__(self)
        self.keys={}
        mod=__import__(modulename)
        self.dirname=os.path.dirname(mod.__file__)
        self.record_types=[]
        for name in dir(_yadata_types):
            obj=getattr(_yadata_types,name)
            if type(obj) is type and issubclass(obj,Record) and (obj is not Record):
                self.record_types.append(obj)
        if os.path.isdir(self.dirname):
            for root,dirs,files in os.walk(self.dirname):
                for name in files:
                    if name.endswith(".yaml"):
                        path=os.path.join(root,name)
                        data=yaml.load(open(path),Loader=yaml.Loader)
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
            return [rec for rec in self if rec == pattern]
    
    def merge(self,dict_to_merge,methods):

        matching_records=self.list_matching(dict_to_merge)
        if not matching_records:
            for typ in self.record_types:
                if typ.is_my_type(dict_to_merge):
                    rec=typ(dict_to_merge)
                    rec.dirty=True
                    rec.save(self)
                    break
            else:
                raise ValueError("Cannot recognise the type of %s" % dict_to_merge)
            return {},[]
        else:
            if len(matching_records)>1:
                raise ValueError("%d matching records for %s" % (len(matching_records),dict_to_merge))
            else:
                matching_record=matching_records[0]
                bounce,log_record=matching_record.merge(dict_to_merge,methods)
                matching_record.save(self)
                return bounce,log_record

