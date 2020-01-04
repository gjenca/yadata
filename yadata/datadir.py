# -*- coding: utf-8 -*-
import os,sys,errno,re
import yaml
import unicodedata
import tempfile
import shutil
from .record import Record

class Datadir(list):

    def append(self,rec):

        list.append(self,rec)
        if "key" in rec:
            self.keys[rec["key"]]=rec

    def __init__(self,dirname):

        list.__init__(self)
        self.keys={}
        self.dirname=dirname
        if os.path.isdir(dirname):
            for root,dirs,files in os.walk(dirname):
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

        if "key" in pattern and pattern["key"] in self.keys:
            return [self.keys[pattern["key"]]]
        else:
            return [rec for rec in self if rec == pattern]
