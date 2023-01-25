from yadata.command.command import YadataCommand
import sys
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

    data_in=True
    data_out=True

    def __init__(self,ns):
        
        super(Sort,self).__init__(ns)
        if not self.ns.sort_key:
            raise ValueError("sort: no key(s) given")
        self.mods={}
        for m in self.ns.module:
            self.mods[m]=__import__(m)
        self.cmp_keys=keys_to_cmp(tuple(self.ns.sort_key))

    def execute(self,it):

        l_other=[]
        if self.ns.restrict_to_type:
            self.ns.restrict=f'_type=="{self.ns.restrict_to_type}"'
        if self.ns.restrict:
            l=[]
            l_orig=list(it)
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
            l=list(it)
        l.sort(key=cmp_to_key(self.cmp_keys))
        for rec in l:
            yield rec
        for rec in l_other:
            yield rec



