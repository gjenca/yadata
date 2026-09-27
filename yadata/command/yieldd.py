from yadata.command.command import YadataCommand
from yadata.utils.misc import Argument

class Yield(YadataCommand):
    """reads object stream, evaluates a python term in a namespace where
the current record is called 'self'. Writes the resulting objects to an object stream.
"""

    name="yield"

    arguments=(
        Argument("term",help="python term"),
        Argument("-g","--generator",action="store_true",help="this is not an object, but a generator"),
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
        for rec in it:
            d=dict({'self':rec})
            d.update(self.mods)
            d["_type"]=type(rec).__name__
            objout=eval(self.ns.term,d)
            if self.ns.generator:
                for obj in objout:
                    yield obj
            else:
                yield objout
