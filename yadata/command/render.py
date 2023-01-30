import sys
import re
import yadata.utils.sane_yaml as sane_yaml
from jinja2 import Template,FileSystemLoader,Environment
from yadata.command.command import YadataCommand
from yadata.utils.compare import make_key
from yadata.utils.misc import Argument
from functools import lru_cache
from collections import defaultdict



def sortfilter(value,*args):

    ret=list(value)
    ret.sort(key=make_key(args))
    return ret


class Render(YadataCommand):
    """reads YAML stream, renders records using a jinja2 template, outputs YAML stream
"""

    name="render"

    arguments=(
        Argument("-e","--extra-yaml",help="additional yaml to pass to template; the data is available as `extra` "),
        Argument("-t","--template-dir",default="./templates",help="directory with templates; default: ./templates"),
        Argument("-s","--soft-references",action="store_true",help="do not fail for missing references"),
        Argument("-p","--jinja-prefix",default="#",help="jinja2 line statement prefix (default: #, for markdown: %%)"),
        Argument("template",help="template file"),
    )

    data_in=True
    data_out=False

    def __init__(self,ns):
        self.ns=ns
        if self.ns.template.endswith('.md'):
            self.ns.jinja_prefix='%%'
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
      
        # use itertools.tee, maybe?
        records=list(it)
        key_dict={}
        # Create key dictionary
        for rec in records:
            if "_key" in rec:
                key_dict[rec.yadata_tag,rec["_key"]]=rec
        edge_tags=defaultdict(lambda:[])
        for rec in records:
            for otm in rec._one_to_many:
                if type(rec[otm.fieldname]) is str:
                    m=re.match('(?P<key>[^;]*);?(?P<tags>.*)',rec[otm.fieldname])
                    other_key=m.group('key')
                    tags=m.group('tags')
                else:
                    other_key=rec[otm.fieldname]
                    tags=''
                other_yadata_tag=otm.inverse_type.yadata_tag
                if (other_yadata_tag,other_key) in key_dict:
                    other=key_dict[other_yadata_tag,other_key]
                elif self.ns.soft_references:
                    continue
                else:
                    raise KeyError(f'render: {other_key} missing, of type {other_yadata_tag} referenced in record {rec["_key"]} (try --soft-references?)')
                if tags:
                    for edge_tag in tags.split(','):
                        edge_tags[(otm.fieldname,rec['_key'],other_key)].append(edge_tag)
                        edge_tags[(otm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                if otm.inverse_fieldname not in other:
                    other[otm.inverse_fieldname]=[]
                other[otm.inverse_fieldname].append(rec)
                if otm.forward:
                    rec[otm.fieldname]=other
            for mtm in rec._many_to_many:
                all_others=[]
                for other_key_tagged in rec[mtm.fieldname]:
                    if type(other_key_tagged) is str:
                        m=re.match('(?P<key>[^;]*);?(?P<tags>.*)',other_key_tagged)
                        other_key=m.group('key')
                        tags=m.group('tags')
                    else:
                        other_key=other_key_tagged
                        tags=''
                    other_yadata_tag=mtm.inverse_type.yadata_tag
                    if (other_yadata_tag,other_key) in key_dict:
                        other=key_dict[other_yadata_tag,other_key]
                    elif self.ns.soft_references:
                        continue
                    else:
                        raise KeyError(f'render: {other_key} of type {other_yadata_tag} missing, referenced in record {rec["_key"]} (try --soft-references?)')
                    if tags:
                        for edge_tag in tags.split(','):
                            edge_tags[(mtm.fieldname,rec['_key'],other_key)].append(edge_tag)
                            edge_tags[(mtm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                    if mtm.inverse_fieldname not in other:
                        other[mtm.inverse_fieldname]=[]
                    other[mtm.inverse_fieldname].append(rec)
                    all_others.append(other)
                if mtm.forward:
                    rec[mtm.fieldname]=all_others
        sort_these=set()
        for rec in records:
            for otm in rec._one_to_many:
                if otm.inverse_sort_by:
                    sort_these.add((otm.inverse_type.yadata_tag,rec[otm.fieldname]['_key'],otm.inverse_fieldname,otm.inverse_sort_by))
        for yadata_tag,key,fieldname,sort_by in sort_these:
                key_dict[yadata_tag,key][fieldname].sort(key=make_key(sort_by))
        env=Environment(loader=FileSystemLoader(self.ns.template_dir),
            line_statement_prefix=self.ns.jinja_prefix)
        env.filters['sort_by']=sortfilter
        t=env.get_template(self.ns.template)
        sys.stdout.write(t.render(records=records,records_by_type=records_by_type,extra=self.extra,edge_tags=edge_tags))




