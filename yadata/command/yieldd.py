from yadata.command.command import YadataCommand
import sys
from yadata.utils.misc import describe_record, Argument, MexGroup

class Yield(YadataCommand):
    """reads object stream, evaluates a python term in a namespace where 
the current record is called 'self'. Writes the resulting objects to an object stream.
"""

    name="yield"

    arguments=(
        Argument("term",help="python term"),
        Argument("-k","--keep-going",action="store_true",help="do not stop when the statement throws an exception"),
        Argument("-m","--module",action="append",default=[],help="python module to import; multiple -m options are possible")
    )

    data_in=True
    data_out=True

    def __init__(self,ns):
        
        super(Yield,self).__init__(ns)
        self.mods={}
        for m in self.ns.module:
            self.mods[m]=__import__(m)


    def execute(self,it):
        exceptions=0
        for i,rec in enumerate(it):
            d=dict({'self':rec})
            d.update(self.mods)
            d["_type"]=type(rec).__name__
            try:
                objout=eval(self.ns.term,d)
            except:
                if self.ns.keep_going:
                    exceptions+=1
                    print("yield: Warning: failed on %s" % describe_record(i,rec), file=sys.stderr)
                    print("yield: The exception was %s" % sys.exc_info()[0], file=sys.stderr)
                else:
                    raise
            yield objout
        if exceptions and not self.ns.failed:
            print("yield: Warning: there were %d exceptions" % exceptions, file=sys.stderr)
            

                
        
        
