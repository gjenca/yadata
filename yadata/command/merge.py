# -*- coding: utf-8 -*-

import sys

from yadata.command.command import YadataCommand
from yadata import Datadir
import yadata.utils.sane_yaml as sane_yaml
from yadata.utils.misc import describe_record, strip_accents, Argument, MexGroup
from yadata.command.command import YadataCommand
import difflib

def isjunk(s):
    return s.isspace()


class Merge(YadataCommand):
    """reads YAML stream, merges records with datadir - see the docs for merge rules
"""
   
    name="merge"

    arguments=(
        Argument("datadir",help="data directory"),
        Argument("-u","--union",help="take union of lists - original and new",
            dest="uname",action="append",default=[]),
        Argument("-s","--set",help="replace orginal value by new value",
            dest="sname",action="append",default=[]),
        Argument("-d","--delete",help="delete this field",
            dest="dname",action="append",default=[]),
        MexGroup(
            Argument("-v","--verbose",action="store_true",help="be verbose"),
            Argument("-q","--quiet",action="store_true",help="be quiet")
        ),
        Argument("-b","--bounced",action="store_true",help="write bounced fields to a mergeable YAML stream"),
    )

    def __init__(self,ns):
        super(Merge,self).__init__(ns)
        self.fields_to_change=self.ns.uname+self.ns.sname+self.ns.dname
        if len(self.fields_to_change)>len(set(self.fields_to_change)):
            raise DataError("merge: duplicite fieldnames in options")
        self.datadir=Datadir(self.ns.datadir)
        self.methods={}

        for field_names,method_name in (
                (self.ns.sname,"set"),
                (self.ns.dname,"delete"),
                (self.ns.uname,"union"),
            ):
            for field_name in field_names:
                self.methods[field_name]=method_name
        self.verbose_level=1
        if self.ns.verbose:
            self.verbose_level=2
        if self.ns.quiet:
            self.verbose_level=0

    def execute(self):

        for i,rec in enumerate(sane_yaml.load_all(sys.stdin)):
            bounced=self.datadir.merge(rec,self.methods,verbose_level=self.verbose_level)
            if bounced and self.ns.bounced:
                print("---")
                sys.stdout.write(sane_yaml.dump(bounced))
        
