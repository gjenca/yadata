# -*- coding: utf-8 -*-

import sys
import yadata.utils.sane_yaml as sane_yaml
from jinja2 import Template,FileSystemLoader,Environment
# pybtex API changed in version 0.20
from yadata.command.command import YadataCommand
from yadata.utils.compare import keys_to_cmp
from yadata.utils.misc import Argument



class Render(YadataCommand):
    """reads YAML stream, renders records using a jinja2 template, outputs YAML stream
"""

    name="render"

    arguments=(
        Argument("-e","--extra-yaml",help="additional yaml to pass to template; the data is available as `extra` "),
        Argument("-t","--template-dir",default="./templates",help="directory with templates; default: ./templates"),
        Argument("template",help="template file"),
    )

    def __init__(self,ns):
        self.ns=ns
        if ns.extra_yaml:
            self.extra=sane_yaml.load(ns.extra_yaml)
        else:
            self.extra=None

    def execute(self):
        
        records=list(sane_yaml.load_all(sys.stdin))
        env=Environment(loader=FileSystemLoader(self.ns.template_dir),
            line_statement_prefix="#")
        t=env.get_template(self.ns.template)
        sys.stdout.write(t.render(records=records,extra=self.extra))




