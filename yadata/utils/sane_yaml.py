# -*- coding: utf-8 -*-
import yaml
import functools
import yadata.record

def construct_yaml_str(self, node):
    return self.construct_scalar(node)

# Override the default string handling function
# to always return unicode objects
yaml.Loader.add_constructor('tag:yaml.org,2002:str', construct_yaml_str)
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:str', construct_yaml_str)

def unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=uni)
    return node

# This is necessary to dump ASCII string normally
yaml.add_representer(str, unicode_representer)

def load_all(f,**kwargs):
    for d in yaml.load_all(f,Loader=yaml.Loader,**kwargs):
        yield d

yaml_load=yaml.load

dump=functools.partial(yaml.dump,allow_unicode=True,default_flow_style=False,sort_keys=False)
load=yaml.safe_load

