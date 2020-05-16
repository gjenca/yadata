# -*- coding: utf-8 -*-

from yadata.command.command import YadataCommand
import sys
import yadata.utils.sane_yaml as sane_yaml
from yadata.utils.compare import keys_to_cmp,cmp_to_key
from yadata.utils.misc import Argument,MexGroup


class Sort(YadataCommand):
    """reads YAML stream, sorts the records in input stream according to given fields, outputs YAML stream
"""

    name="sort"

    arguments=(
        Argument("-k","--sort-key",action="append",help="either fieldname or ~fieldname"),
        Argument("-m","--module",action="append",default=[],help="python module to import"),
        MexGroup(
            Argument("-t","--restrict-to-type",action="store",help="sort records of this type, then output the other records"),
            Argument("-r","--restrict",action="store",help="sort only those records for which the RESTRICT python term evaluates to True, output them, then output the other records"),
            ),
    )

    def __init__(self,ns):
        
        super(Sort,self).__init__(ns)
        if not self.ns.sort_key:
            raise ParameterError("sort: no key(s) given")
        self.mods={}
        for m in self.ns.module:
            self.mods[m]=__import__(m)

        self.cmp_keys=keys_to_cmp(self.ns.sort_key)

    def execute(self):

        l_other=[]
        if self.ns.restrict_to_type:
            self.ns.restrict=f'_type=="{self.ns.restrict_to_type}"'
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




