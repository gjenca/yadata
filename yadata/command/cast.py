from yadata.command.command import YadataCommand
from yadata.utils.misc import Argument
try:
    import _yadata_types
except ImportError:
    pass

class Cast(YadataCommand):
    """reads YAML stream, creates objects of a given type from each object, outputs YAML stream"""

    name="cast"

    arguments=(
        Argument("type",help="Create objects of this type."),
    )

    data_in=True
    data_out=True


    def execute(self,it):
        try:
            type_to_cast=getattr(_yadata_types,self.ns.type)
        except NameError:
            raise ModuleNotFoundError("cast: no _yadata_types module in the current directory")
        except AttributeError:
            raise AttributeError(f"cast: no type {self.ns.type} in _yadata_types")
        for rec in it:
            yield type_to_cast(rec)
             
        
