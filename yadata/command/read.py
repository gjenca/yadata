# -*- coding: utf-8 -*-

from yadata.command.command import YadataCommand
import os,sys

import yadata.utils.sane_yaml as sane_yaml
from yadata.utils.misc import Argument, MexGroup
from yadata import Datadir

class Read(YadataCommand):
    """reads records from datadir, outputs them as a YAML stream
"""

    name="read"
    
    arguments=(
        Argument("datadir",help="data directory"),
    )

    data_in=False
    data_out=True

    def execute(self,it=None):
        dd=Datadir(self.ns.datadir)
        for rec in dd:
            yield rec 
