# -*- coding: utf-8 -*-

from yadata.utils.misc import Argument,MexGroup

def _add_arguments(something_with_arguments,subparser):
        
        for arg in something_with_arguments.arguments:
            if type(arg) is Argument:
                subparser.add_argument(*arg.args,**arg.kwargs)
            elif type(arg) is MexGroup:
                group=subparser.add_mutually_exclusive_group()
                _add_arguments(arg,group)

class YadataCommand(object):

    def __init__(self,ns):
        self.ns=ns
    
    @classmethod
    def add_arguments(cls,subparser):
        _add_arguments(cls,subparser)

        
        
