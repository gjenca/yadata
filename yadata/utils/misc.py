# -*- coding: utf-8 -*-


def describe_record(i,rec):
    
    return "record no. %d (_key=%s)" % (i,rec.get("_key","None")) 

class Argument(object):

    def __init__(self,*args,**kwargs):
        self.args=args
        self.kwargs=kwargs

    @property
    def parameter(self):
        if "action" in self.kwargs and self.kwargs["action"]=='store_true':
            return ""
        if "dest" in self.kwargs:
            return self.kwargs["dest"].upper().replace("-","_")
        for arg in self.args:
            if arg.startswith("--"):
                return arg[2:].upper().replace("-","_")
        return ""

class MexGroup(object):

    def __init__(self,*args):
        self.arguments=tuple(args)
