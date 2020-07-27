# -*- coding: utf-8 -*-

from yadata.command.command import YadataCommand
import sys
from yadata.utils.misc import describe_record, Argument
import _yadata_types

class Cast(YadataCommand):
    """reads YAML stream, creates objects of a given type from each object, outputs"""

    name="append"

    arguments=(
        Argument("type",help="Create objects of this type."),
    )

    data_in=True
    data_out=True


    def execute(self,it):
        type_to_cast=getattr(_yadata_types,self.ns.type)
        for i,rec in enumerate(it):
            yield type_to_cast(rec)
             
        
