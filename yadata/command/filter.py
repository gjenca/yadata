# -*- coding: utf-8 -*-


from yadata.command.command import YadataCommand
import sys
import yadata.utils.sane_yaml as sane_yaml
from yadata.utils.misc import describe_record,Argument

class Filter(YadataCommand):
    """reads YAML stream, evaluates a python expression in the context of the each record,
    outputs YAML stream with records for which expression returns True"""
    
    name="filter"

    arguments=(
        Argument("expr",help="python expression"),
        Argument("-f","--failed",action="store_true",help="output only the failed records,supress error message"),
        Argument("-m","--module",action="append",default=[],help="python module to import"),
        Argument("-k","--keep-going",action="store_true",help="do not stop when the eval(expr) throws an exception"),
        )

    data_in=True
    data_out=True

    def __init__(self,ns):
        
        super(Filter,self).__init__(ns)
        self.mods={}
        for m in self.ns.module:
            self.mods[m]=__import__(m)

    def execute(self,it):
        exceptions=0
        for i,rec in enumerate(it):
            try:
                d=dict(rec)
                d.update(self.mods)
                d["_type"]=type(rec).__name__
                tf=eval(self.ns.expr,d)
            except:
                if self.ns.failed:
                    if '__builtins__' in rec:    
                        del rec['__builtins__']
                    yield rec
                elif self.ns.keep_going:
                    exceptions+=1
                    print("filter: Warning: failed on %s" % describe_record(i,rec), file=sys.stderr)
                    print("filter: The exception was %s" % sys.exc_info()[0], file=sys.stderr)
                else:
                    raise
            else:
                if not self.ns.failed and tf:
                    yield rec

        if exceptions and not self.ns.failed:
            print("exec: Warning: there were %d exceptions" % exceptions, file=sys.stderr)
            
        
        
