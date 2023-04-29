import sys
import inspect


import yadata.utils.sane_yaml as sane_yaml
from yadata.command.command import YadataCommand
from yadata.utils.misc import Argument
from yadata.record import Record


class Import(YadataCommand):
    """reads Excel spreadskeet from a file, outputs YAML stream of records
"""

    name="import"

    arguments=(
        Argument("infile",help="Excel filename to read"),
    )

    data_in=False
    data_out=True

    def __init__(self,ns):
        self.ns=ns

    def execute(self,it=None):
       
        # This is an expensive import, so we move it here
        import openpyxl
        wb=openpyxl.load_workbook(self.ns.infile)
        tag_to_type={}
        import _yadata_types
        for name,obj in inspect.getmembers(_yadata_types):
            if inspect.isclass(obj) and issubclass(obj,Record):
                tag_to_type[obj.yadata_tag]=obj
        for sheet in wb:
            if sheet.title not in tag_to_type:
                    print(f'Sheet name {sheet.title} in {self.ns.infile} is not a yadata tag',file=sys.stderr)
                    sys.exit(1)
            cls=tag_to_type[sheet.title]
            rows_iter=sheet.rows
            first_row=rows_iter.__next__()
            names=[cell.value for cell in first_row]
            for row in rows_iter:
                d={}
                for name,cell in zip(names,row):
                    d[name]=cell.value
                rec=cls(d)
                yield rec
