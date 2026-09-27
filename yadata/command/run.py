import sys
import os
import subprocess

from yadata.command.command import YadataCommand
from yadata.utils.misc import Argument


class Run(YadataCommand):
    """reads YAML stream, runs a shell command on every record, with environment
given by the record. For every field, the value is represented by 'YADATA_field=value' in the environment.
"""
   
    name="run"

    arguments=(
        Argument("shell_command",help="shell command"),
    )

    data_in=True
    data_out=False
    
    def execute(self,it):

        for i,rec in enumerate(it):
            d=dict(os.environ)
            for field in rec:
                d[f'YADATA_{field}']=f'{rec[field]}'
            subprocess.run(self.ns.shell_command,shell=True,env=d,check=False)
        return None

            
            
        
