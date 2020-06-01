# -*- coding: utf-8 -*-


from yadata.command.command import YadataCommand
import sys
from yadata.utils.misc import Argument

class Type(YadataCommand):
    '''reads YAML stream of typed objects, outputs YAML stream with objects of one of the given type(s)'''
    
    name='type'

    arguments=(
        Argument('-u','--keep-untyped',action='store_true',help='keep untyped objects (plain dicts)'),
        Argument('types',action='append',help='selected types'),
        )

    def __init__(self,ns):
        
        super(Type,self).__init__(ns)

    data_in=True
    data_out=True

    def execute(self,it):
        for i,rec in enumerate(it):
            if (self.ns.keep_untyped and type(rec) is dict) or \
                type(rec).__name__ in self.ns.types:
                    yield rec
        
