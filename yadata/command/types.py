# -*- coding: utf-8 -*-


from yadata.command.command import YadataCommand
import sys
import yadata.utils.sane_yaml as sane_yaml
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


    def execute(self):
        for i,rec in enumerate(sane_yaml.load_all(sys.stdin)):
            if (self.ns.keep_untyped and type(rec) is dict) or \
                type(rec).__name__ in self.ns.types:
                print('---')
                sys.stdout.write(sane_yaml.dump(rec))

        
