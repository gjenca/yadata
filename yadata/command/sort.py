# -*- coding: utf-8 -*-

from yadata.command.command import YadataCommand
import sys
import yadata.utils.sane_yaml as sane_yaml
from yadata.utils.compare import keys_to_cmp
from yadata.utils.misc import Argument

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

class Sort(YadataCommand):
    """reads YAML stream, sorts the records in input stream according to given fields, outputs YAML stream
"""

    name="sort"

    arguments=(
        Argument("-k","--sort-key",action="append",help="either fieldname or ~fieldname"),
        Argument("-m","--module",action="append",default=[],help="python module to import"),
        Argument("-r","--restrict",action="store",help="sort only those records for which the RESTRICT python term evaluates to True, output them, then output the other records"),
    )

    def __init__(self,ns):
        self.ns=ns

        if not self.ns.sort_key:
            raise ParameterError("sort: no key(s) given")
        self.mods={}
        for m in self.ns.module:
            self.mods[m]=__import__(m)

        self.cmp_keys=keys_to_cmp(self.ns.sort_key)

    def execute(self):

        l_other=[]
        if self.ns.restrict:
            l=[]
            l_orig=list(sane_yaml.load_all(sys.stdin))
            for rec in l_orig:
                d=dict(rec)
                d.update(self.mods)
                d["_type"]=type(rec).__name__
                tf=eval(self.ns.restrict,d)
                if tf:
                    l.append(rec)
                else:
                    l_other.append(rec)
        else:
            l=list(sane_yaml.load_all(sys.stdin))
        l.sort(key=cmp_to_key(self.cmp_keys))
        for d in l:
            print("---")
            sys.stdout.write(sane_yaml.dump(d))
        for d in l_other:
            print("---")
            sys.stdout.write(sane_yaml.dump(d))




