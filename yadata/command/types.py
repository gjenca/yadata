from yadata.command.command import YadataCommand
import sys
from yadata.utils.misc import Argument
import _yadata_types

class Type(YadataCommand):
    '''reads YAML stream of typed objects, outputs YAML stream with objects of one of the given type(s) or their subclasses'''
    
    name='type'

    arguments=(
        Argument('-u','--keep-untyped',action='store_true',help='keep untyped objects (plain dicts)'),
        Argument('types',nargs='+',help='selected types'),
        )

    def __init__(self,ns):
        
        super(Type,self).__init__(ns)

    data_in=True
    data_out=True

    def execute(self,it):
        types=[getattr(_yadata_types,typename) for typename in self.ns.types]
        for i,rec in enumerate(it):
            if (self.ns.keep_untyped and type(rec) is dict) or \
                    any(issubclass(type(rec),t) for t in types):
                yield rec
        
