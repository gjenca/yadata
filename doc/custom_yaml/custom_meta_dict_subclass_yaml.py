#!/usr/bin/env python3
import sys
import yaml
import re

def MetaRecord(cls):

    def cls_representer(dumper,data):

        return dumper.represent_mapping(cls.yaml_tag,dict(data),flow_style=False)

    def cls_constructor(loader,node):

        dict_value=loader.construct_mapping(node)
        return cls(dict_value)

    yaml.add_representer(cls,cls_representer)
    yaml.add_constructor(cls.yaml_tag,cls_constructor)

    return cls

@MetaRecord
class Record(dict):

    yaml_tag='!Record'

    def __init__(self,d):
        
        dict.__init__(self,d)
        self.some_tmp_attribute=True



out=yaml.dump(Record({'meno':'Gejza','priezvisko':'Jenča'}),allow_unicode=True)
print(out)
r=yaml.load(out,Loader=yaml.Loader)
r['tags']=['value1','value2']
print(type(r),r)
out=yaml.dump(r,allow_unicode=True,default_flow_style=None)
print(out)
