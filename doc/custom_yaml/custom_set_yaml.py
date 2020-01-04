#!/usr/bin/env python3
import sys
import yaml
import re


def set_representer(dumper,data):

    return dumper.represent_sequence('!set',list(data),flow_style=True)

def set_constructor(loader,node):

    list_value=loader.construct_sequence(node)
    return set(list_value)

yaml.add_representer(set,set_representer)
yaml.add_constructor('!set',set_constructor)

out=yaml.dump(set([1,2,3]))
print(out)
s=yaml.load(out,Loader=yaml.Loader)
print(type(s),s)
