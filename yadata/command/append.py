from yadata.command.command import YadataCommand
import sys
from yadata.utils.misc import describe_record, Argument

class Append(YadataCommand):
    """reads YAML stream, appends all strings in the list to the value of a field, outputs YAML stream
"""

    name="append"

    arguments=(
        Argument("fieldname",help="Field name. Value must be a 'list of strings', if it does exist. If it does not, it is created."),
        Argument("string",nargs="+",help="these strings are appended to the value"),
    )

    data_in=True
    data_out=True

    def execute(self,it):
        for i,rec in enumerate(it):
            if self.ns.fieldname in rec:
                value=rec[self.ns.fieldname]
                if type(value) is not list:
                    raise TypeError("append: expecting a list under %s in %s, got %s instead" %
                        (self.ns.fieldname,describe_record(i,rec),type(value)))
                value.extend(self.ns.string)
                value=list(set(value))
                rec[self.ns.fieldname]=value
            else:
                rec[self.ns.fieldname]=[s for s in self.ns.string]
            yield rec
                
        
        
