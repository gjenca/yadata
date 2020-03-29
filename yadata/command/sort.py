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
    )

    def __init__(self,ns):
        self.ns=ns

        if not self.ns.sort_key:
            raise ParameterError("sort: no key(s) given")

        self.cmp_keys=keys_to_cmp(self.ns.sort_key)

    def execute(self):

        l=list(sane_yaml.load_all(sys.stdin))
        l.sort(key=cmp_to_key(self.cmp_keys))
        for d in l:
            print("---")
            sys.stdout.write(sane_yaml.dump(d))




