#!/usr/bin/env python3
import sys
import yaml
import re

class Record(dict):

    pass

def Record_representer(dumper,data):

    return dumper.represent_mapping('!Record',dict(data),flow_style=False)

def Record_constructor(loader,node):

    dict_value=loader.construct_mapping(node)
    return Record(dict_value)

yaml.add_representer(Record,Record_representer)
yaml.add_constructor('!Record',Record_constructor)

out=yaml.dump(Record({'meno':'Gejza','priezvisko':'Jenca'}))
print(out)
r=yaml.load(out,Loader=yaml.Loader)
print(type(r),r)
