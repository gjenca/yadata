# -*- coding: utf-8 -*-

import sys

from yadata.command.command import YadataCommand
from yadata import Datadir
from yadata.utils.misc import describe_record, Argument, MexGroup
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

    data_in=True
    data_out=True
    
    def __init__(self,ns):
        super(Merge,self).__init__(ns)
        self.fields_to_change=self.ns.uname+self.ns.sname+self.ns.dname
        if len(self.fields_to_change)>len(set(self.fields_to_change)):
            raise ValueError("merge: duplicite fieldnames in options")
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

    def execute(self,it):

        bounced_records_num=0
        bounced_fields_num=0
        for i,rec in enumerate(it):
            bounced,log=self.datadir.merge(rec,self.methods)
            if self.ns.bounced:
                if bounced:
                    yield bounced
            elif self.verbose_level==2:
                bounced_fields=list(bounced.keys())
                if "_key" in bounced_fields:
                    bounced_fields.remove("_key")
                if bounced_fields:
                    print("merge: fields {} in record number {} bounced".format(bounced_fields,i),
                        file=sys.stderr)
                for logentry in log:
                    print(logentry,file=sys.stderr)
            elif self.verbose_level==1 and bounced:
                bounced_records_num+=1
                bounced_fields_num+=len(bounced)-1
        if bounced_records_num and self.verbose_level>0 and not self.ns.bounced:
                print("""{} fields in {} records bounced
use -v to see bounced fields
use -b to create mergeable stream of bounced records""".format(bounced_fields_num,bounced_records_num),
                    file=sys.stderr)

            
        
