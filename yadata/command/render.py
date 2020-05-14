# -*- coding: utf-8 -*-

import sys
import yadata.utils.sane_yaml as sane_yaml
from jinja2 import Template,FileSystemLoader,Environment
# pybtex API changed in version 0.20
from yadata.command.command import YadataCommand
from yadata.utils.compare import keys_to_cmp
from yadata.utils.misc import Argument



class Render(YadataCommand):
    """reads YAML stream, renders records using a jinja2 template, outputs YAML stream
"""

    name="render"

    arguments=(
        Argument("-e","--extra-yaml",help="additional yaml to pass to template; the data is available as `extra` "),
        Argument("-t","--template-dir",default="./templates",help="directory with templates; default: ./templates"),
        Argument("template",help="template file"),
    )

    def __init__(self,ns):
        self.ns=ns
        if ns.extra_yaml:
            self.extra=sane_yaml.load(ns.extra_yaml)
        else:
            self.extra=None

    def execute(self):
        
        records=list(sane_yaml.load_all(sys.stdin))
        for rec in records:
                rec["_type"]=type(rec).__name__
        records_new=[]
        key_dict={}
        for rec in records:
            if "_key" in rec:
                key_dict[rec["_key"]]=rec
            records_new.append(rec)
        records=records_new
        for rec in records:
            for otm in rec._one_to_many:
                other=key_dict[rec[otm.fieldname]]
                if otm.inverse_fieldname not in other:
                    other[otm.inverse_fieldname]=[]
                other[otm.inverse_fieldname].append(rec)
                rec[otm.fieldname]=other
            for mtm in rec._many_to_many:
                all_others=[]
                for other_key in rec[mtm.fieldname]:
                    other=key_dict[other_key]
                    if mtm.inverse_fieldname not in other:
                        other[mtm.inverse_fieldname]=[]
                    other[mtm.inverse_fieldname].append(rec)
                    all_others.append(other)
                rec[mtm_fieldname]=all_others
        env=Environment(loader=FileSystemLoader(self.ns.template_dir),
            line_statement_prefix="#")
        t=env.get_template(self.ns.template)
        sys.stdout.write(t.render(records=records,extra=self.extra))




