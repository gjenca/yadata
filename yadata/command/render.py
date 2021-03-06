# -*- coding: utf-8 -*-

import sys
import re
import yadata.utils.sane_yaml as sane_yaml
from jinja2 import Template,FileSystemLoader,Environment
from yadata.command.command import YadataCommand
from yadata.utils.compare import keys_to_cmp,cmp_to_key
from yadata.utils.misc import Argument
from functools import lru_cache
from collections import defaultdict

@lru_cache
def make_key(key_tuple):

  return cmp_to_key(keys_to_cmp(key_tuple))

class Render(YadataCommand):
    """reads YAML stream, renders records using a jinja2 template, outputs YAML stream
"""

    name="render"

    arguments=(
        Argument("-e","--extra-yaml",help="additional yaml to pass to template; the data is available as `extra` "),
        Argument("-t","--template-dir",default="./templates",help="directory with templates; default: ./templates"),
        Argument("-s","--soft-references",action="store_true",help="do not fail for missing references"),
        Argument("-p","--jinja-prefix",default="#",help="jinja2 line statement prefix (default: #)"),
        Argument("template",help="template file"),
    )

    data_in=True
    data_out=False

    def __init__(self,ns):
        self.ns=ns
        if ns.extra_yaml:
            self.extra=sane_yaml.load(ns.extra_yaml)
        else:
            self.extra=None


    def execute(self,it):

        def records_by_type(typename):
            ret=[]
            for rec in records:
                if typename==type(rec).__name__:
                    ret.append(rec)
            return ret
        
        records=list(it)
        for rec in records:
                rec["_type"]=type(rec).__name__
        #records_new=[]
        key_dict={}
        # Create key dictionary
        for rec in records:
            if "_key" in rec:
                key_dict[rec["_key"]]=rec
            #records_new.append(rec)
        #records=records_new
        edge_tags=defaultdict(lambda:[])
        for rec in records:
            for otm in rec._one_to_many:
                m=re.match('(?P<key>[^;]*);?(?P<tags>.*)',rec[otm.fieldname])
                other_key=m.group('key')
                if other_key in key_dict:
                    other=key_dict[other_key]
                elif self.ns.soft_references:
                    continue
                else:
                    raise KeyError(f'render: {other_key} missing, referenced in record {rec["_key"]} (try --soft-references?)')
                if m.group('tags'):
                    for edge_tag in m.group('tags').split(','):
                        edge_tags[(otm.fieldname,rec['_key'],other_key)].append(edge_tag)
                        edge_tags[(otm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                if otm.inverse_fieldname not in other:
                    other[otm.inverse_fieldname]=[]
                other[otm.inverse_fieldname].append(rec)
                other[otm.inverse_fieldname].sort(key=make_key(otm.inverse_sort_by))
                rec[otm.fieldname]=other
            for mtm in rec._many_to_many:
                all_others=[]
                for other_key_tagged in rec[mtm.fieldname]:
                    m=re.match('(?P<key>[^;]*);?(?P<tags>.*)',other_key_tagged)
                    other_key=m.group('key')
                    if other_key in key_dict:
                        other=key_dict[other_key]
                    elif self.ns.soft_references:
                        continue
                    else:
                        raise KeyError(f'render: {other_key} missing, referenced in record {rec["_key"]} (try --soft-references?)')
                    if m.group('tags'):
                        for edge_tag in m.group('tags').split(','):
                            edge_tags[(mtm.fieldname,rec['_key'],other_key)].append(edge_tag)
                            edge_tags[(mtm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                    if mtm.inverse_fieldname not in other:
                        other[mtm.inverse_fieldname]=[]
                    other[mtm.inverse_fieldname].append(rec)
                    all_others.append(other)
                rec[mtm.fieldname]=all_others
        
        env=Environment(loader=FileSystemLoader(self.ns.template_dir),
            line_statement_prefix=self.ns.jinja_prefix)
        t=env.get_template(self.ns.template)
        sys.stdout.write(t.render(records=records,records_by_type=records_by_type,extra=self.extra,edge_tags=edge_tags))




