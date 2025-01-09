import sys
import re
import yadata.utils.sane_yaml as sane_yaml
from jinja2 import Template,FileSystemLoader,Environment
from yadata.command.command import YadataCommand
from yadata.utils.compare import make_key
from yadata.utils.misc import Argument
from functools import cache
from collections import defaultdict
from yadata.record import Record
from yadata.utils.misc import _yadata_log

def strip_document_end_marker(s):
   if s.endswith('\n...\n'):
       return s[:-5]

def sortfilter(value,*args):

    ret=list(value)
    ret.sort(key=make_key(args))
    return ret

def collect_backrefs(key,backrefs):

    ret=set()
    bag=set([key])
    while bag:
        next_key=bag.pop()
        if next_key in ret:
            continue
        ret.add(next_key)
        bag.update(backrefs[next_key])
    return ret

def split_tags(reftags):
        
        if type(reftags) is str:
            m=re.match(r'(?P<key>[^;]*);?(?P<tags>.*)',reftags)
            other_key=m.group('key')
            tags=m.group('tags')
        else:
            other_key=reftags
            tags=''
        
        return other_key,tags

def collect_otm(C):

    ret=[]
    for cls in C.__mro__:
        if '_one_to_many' in dir(cls):
            ret.extend(cls._one_to_many)
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

        @cache
        def records_by_type(typename):
            ret=[]
            for rec in records:
                supernames=[cls.__name__ for cls in type(rec).__mro__]
                if typename in supernames:
                    ret.append(rec)
            return ret

        def record_by_tag_and_key(yadata_tag,key):
            
            return key_dict[yadata_tag,key]

        def render_option(value,selected):

            if type(value) is bool:
                attr_value={True:'true',False:'false'}[value]
                show_value={True:'yes',False:'no'}[value]
            elif value is None:
                attr_value='null'
                show_value='--'
            elif type(value) is str:
                attr_value=r'&quot;'+value+r'&quot;'
                show_value=value
            if selected:
                return f'<option value="{attr_value}" selected="selected">{show_value}</option>'
            else:
                return f'<option value="{attr_value}">{show_value}</option>'

        def field_input(rec,field,typename=None):
            
            value=rec.get(field,None)
            name=';'.join((rec.yadata_tag[1:],rec['_key'],field))
            yaml_value=sane_yaml.dump(value)
            yaml_value=strip_document_end_marker(yaml_value)
            fstring_l=[]
            if type(value) in (int,str,float):
                fstring_l.append(
                        r'<input type="text" name="{name}" id="{name}" value="{value}">'
                        )
            elif type(value) is bool:
                fstring_l.append(r'<select name="{name}" id="{name}" onchange="this.form.submit()">')
                for opt in (True,False):
                    fstring_l.append(render_option(opt,opt==value))
                fstring_l.append(r'</select>')
            else:
                for otm in collect_otm(type(rec)):
                    if field==otm.fieldname:
                        fstring_l.append(r'<select name="{name}" id="{name}" onchange="this.form.submit()">')
                        value=rec.get(field,None)
                        fstring_l.append(render_option(None,value is None))
                        if value!=None:
                            value=value['_key']
                        typename=otm.inverse_type.__name__
                        for opt_rec_key in sorted(opt_rec['_key'] for opt_rec in records_by_type(typename)):
                            fstring_l.append(render_option(opt_rec_key,value==opt_rec_key))
                        fstring_l.append(r'</select>')
            fstring="\n".join(fstring_l)
            return fstring.format(name=name,value=yaml_value)

        # use itertools.tee, maybe?
        records=list(it)
        key_dict={}
        backrefs=defaultdict(lambda:set())
        zap_these=set()
        # Create key dictionary
        for rec in records:
            if "_key" in rec:
                key_dict[rec.yadata_tag,rec["_key"]]=rec
        edge_tags=defaultdict(lambda:[])
        # Resolve OTM fields; a record with a dangling OTM field is to be zapped
        for rec in records:
            # All otm fields must be valid
            valid=True
            for otm in rec._one_to_many:
                # A missing OTM field is *not* dangling
                if otm.fieldname not in rec:
                    continue
                # An OTM field explicitely set to None is *not* dangling
                if rec[otm.fieldname] is None:
                    continue
                other_key,tags=split_tags(rec[otm.fieldname])
                other_yadata_tag=otm.inverse_type.yadata_tag
                if (other_yadata_tag,other_key) not in key_dict:
                    if self.ns.soft_references:
                        zap_these.add((rec.yadata_tag,rec['_key']))
                        _yadata_log('zapping',rec['_key'],'because of',other_key)
                        valid=False
                        break
                    else:
                        raise KeyError(f'render: {other_key} missing, of type {other_yadata_tag} referenced in record {rec["_key"]} (try --soft-references?)')
            if not valid:
                continue
            # We know that all OTM fields are valid or missing or None now; we may resolve them
            for otm in rec._one_to_many:
                # OTM field is missing or None
                if otm.fieldname not in rec or \
                    rec[otm.fieldname] is None:
                    continue
                other_key,tags=split_tags(rec[otm.fieldname])
                other_yadata_tag=otm.inverse_type.yadata_tag
                other=key_dict[other_yadata_tag,other_key]
                backrefs[other_yadata_tag,other_key].add((rec.yadata_tag,rec['_key']))
                if tags:
                    for edge_tag in tags.split(','):
                        edge_tag=edge_tag.strip()
                        edge_tags[(otm.fieldname,rec['_key'],other_key)].append(edge_tag)
                        edge_tags[(otm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                if otm.inverse_fieldname not in other:
                    other[otm.inverse_fieldname]=[]
                other[otm.inverse_fieldname].append(rec)
                rec[otm.fieldname]=other
        # Add to zap_this all records that refer to records with dangling OTM fields
        for zap_this in list(zap_these):
            backrefs_deep=collect_backrefs(zap_this,backrefs)
            zap_these.update(backrefs_deep)
        # Remove zap_this from the list
        records=[
            record
            for record in records
            if (record.yadata_tag,record['_key']) not in zap_these
        ]
        # Remove zap_this from the key_dict (maybe this is not needed)
        for yadata_tag,key in zap_these:
            del key_dict[yadata_tag,key]
        # Remove zap_this records from inverse fields
        for rec in records:
            for inverse_field in rec._inverse:
                rec[inverse_field]=[inv for inv in rec[inverse_field]
                    if (inv.yadata_tag,inv['_key']) not in zap_these]
        # Everything should be consistent now, no dangling OTM fields
        # Resolve MTM fields
        # It seems to me that MTM fields sould not be allowed to be missing or None;
        # they may be [] but this is not a problem
        for rec in records:
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
                            edge_tag=edge_tag.strip()
                            edge_tags[(mtm.fieldname,rec['_key'],other_key)].append(edge_tag)
                            edge_tags[(mtm.inverse_fieldname,other_key,rec['_key'])].append(edge_tag)
                    if mtm.inverse_fieldname not in other:
                        other[mtm.inverse_fieldname]=[]
                    other[mtm.inverse_fieldname].append(rec)
                    all_others.append(other)
                rec[mtm.fieldname]=all_others
        # Sorting here is deprecated; sorting belongs to
        # templates. This will be removed in the released version.
        sort_these=set()
        for rec in records:
            for otm in rec._one_to_many:
                if otm.inverse_sort_by:
                    sort_these.add((otm.inverse_type.yadata_tag,rec[otm.fieldname]['_key'],otm.inverse_fieldname,otm.inverse_sort_by))
        for yadata_tag,key,fieldname,sort_by in sort_these:
                key_dict[yadata_tag,key][fieldname].sort(key=make_key(sort_by))
        env=Environment(loader=FileSystemLoader(self.ns.template_dir),
            line_statement_prefix=self.ns.jinja_prefix,
            extensions=['jinja2.ext.loopcontrols'],
                        )
        env.filters['sort_by']=sortfilter
        t=env.get_template(self.ns.template)
        # I probably do not need records=records here
        # Rename records_by_type (?)
        #print('edge_tags',edge_tags,file=sys.stderr)
        sys.stdout.write(
            t.render(
                records=records,
                records_by_type=records_by_type,
                record_by_tag_and_key=record_by_tag_and_key,
                field_input=field_input,
                extra=self.extra,
                edge_tags=edge_tags,
            ))




