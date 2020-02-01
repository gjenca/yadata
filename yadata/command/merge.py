# -*- coding: utf-8 -*-

import sys

from yacite.types import Datadir
from yacite.exception import *
from yacite.types import BibRecord
import yacite.utils.sane_yaml as sane_yaml
from yacite.utils.misc import describe_record, strip_accents, Argument, MexGroup
from yacite.command.command import YaciteCommand
import difflib

def isjunk(s):
    return s.isspace()

def check_bounced(rec,match,key):

    if key!="authors" and (type(rec[key]) is list) and (type(match[key]) is list):
        return set(rec[key])!=set(match[key])
    return rec[key]!=match[key]


def check_strongly_bounced(rec,match,key):

    if key == "authors":
        return not match.same_authors(rec,preprocess=strip_accents)
    elif all(t in (str,str) for t in (type(rec[key]),type(match[key]))):
        ratio=difflib.SequenceMatcher(isjunk,rec[key].lower(),match[key].lower()).ratio()
        return ratio<0.50
    elif type(rec[key]) is list and type(match[key]) is list:
        return set(rec[key])==set(match[key])
    else:
        return rec[key]!=match[key]
        

class Merge(YaciteCommand):
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
        Argument("-v","--verbose",action="store_true",help="be verbose"),
        MexGroup(
            Argument("-n","--new",action="store_true",help="write only new records to a mergeable YAML stream; do not actually change datadir"),
            Argument("-o","--old",action="store_true",help="write only already existing records to a mergeable YAML stream; do not actually datadir"),
            Argument("-b","--bounced",action="store_true",help="write bounced fields to a mergeable YAML stream"),
            Argument("-B","--strongly-bounced",action="store_true",help="write strongly bounced fields to a mergeable YAML stream")
        ),
        Argument("-q","--quiet",action="store_true",help="be quiet")
    )

    def __init__(self,ns):
        super(Merge,self).__init__(ns)
        self.fields_to_change=self.ns.uname+self.ns.sname+self.ns.dname
        if len(self.fields_to_change)>len(set(self.fields_to_change)):
            raise DataError("merge: duplicite fieldnames in options")
        self.datadir=Datadir(self.ns.datadir)

    def execute(self):

        # 1. statistics
        bounced_fields_num=0
        bounced_records_num=0
        glob_bounced_fields=[]
        # 2. new_record, new_field, set, union, delete
        for i,rec in enumerate(sane_yaml.load_all(sys.stdin)):
            # 2.0. prepare:
            matches=self.datadir.list_matching(rec)
            if len(matches)>1:
                raise DataError("merge: %s in stream matches multiple records in datadir; the keys are: %s" \
                    % (describe_record(i,rec),",".join(match["key"] for match in matches)))
            record_bounced=False
            if not matches:
                # 2.1 new record
                if self.ns.new:
                    print("---")
                    sys.stdout.write(sane_yaml.dump(rec))
                elif not self.ns.old:
                    newrecord=BibRecord(rec,datadir=self.datadir)
                    newrecord.dirty=True
                    newrecord.save()
                    self.datadir.append(newrecord)
                    if not self.ns.quiet:
                        print("merge: Created new record: %s" % newrecord.path, file=sys.stderr)
            else:
                match=matches[0]
                if self.ns.old:
                    print("---")
                    sys.stdout.write(sane_yaml.dump(rec))
                    continue
                # 2.2. count bounced fields
                bounced_fields=[]
                strongly_bounced_fields=[]
                for field_name in rec:
                    if field_name in match and check_bounced(rec,match,field_name) and field_name not in \
                        self.fields_to_change:
                            bounced_fields_num+=1
                            record_bounced=True
                            bounced_fields.append(field_name)
                            if check_strongly_bounced(rec,match,field_name):
                                strongly_bounced_fields.append(field_name)
                            if field_name not in glob_bounced_fields:
                                glob_bounced_fields.append(field_name)
                                glob_bounced_fields.sort()
                if (self.ns.bounced and bounced_fields) or \
                    (self.ns.strongly_bounced and strongly_bounced_fields):
                    print("---")
                    d_rec={}
                    d_match={}
                    if self.ns.bounced:
                        bfs=bounced_fields
                    else:
                        bfs=strongly_bounced_fields
                    for bf in bfs:
                        d_rec[bf]=rec[bf]
                        d_match[bf]=match[bf]
                    d_rec["key"]=match["key"]
                    fs=None
                    if all(type(x) in (int,str,str) for x in list(d_match.values())):
                        fs=False
                    for line in sane_yaml.dump(d_match,default_flow_style=fs).split("\n"):
                        if line:
                            print("#",line)
                    if all(type(x) in (int,str,str) for x in list(d_rec.values())):
                        fs=False
                    sys.stdout.write(sane_yaml.dump(d_rec,default_flow_style=fs))
                if self.ns.verbose and bounced_fields:
                    print("merge: %s, file '%s':fields %s bounced" \
                    % (describe_record(i,rec),match.path,",".join(bounced_fields)), file=sys.stderr)
                # 2.3. new_field
                for field_name in rec:
                    if field_name not in match:
                        if not self.ns.quiet:
                            print("merge: SET %s[%s] to %s (new field)" \
                            % (match["key"],field_name,rec[field_name]), file=sys.stderr)
                        match[field_name]=rec[field_name]
                # 2.4. set
                for field_name in self.ns.sname:
                    if field_name in rec and field_name in match and check_bounced(match,rec,field_name):
                        if not self.ns.quiet:
                            print("merge: SET %s[%s] to %s" \
                                %(match["key"],field_name,rec[field_name]), file=sys.stderr)
                        match[field_name]=rec[field_name]
                # 2.5. union
                for field_name in self.ns.uname:
                    if type(rec[field_name]) is list and type(match[field_name]) is list:
                        if not set(match[field_name])>=set(rec[field_name]):
                            match[field_name].extend(rec[field_name])
                            match[field_name]=list(set(match[field_name]))
                            if not self.ns.quiet:
                                print("merge: SET %s[%s] to %s (union)" \
                                    %(match["key"],field_name,match[field_name]), file=sys.stderr)
                    else:
                        raise DataError(
                            "merge: union of non-lists requested: %s in stream, file='%s', name='%s"
                            % (describe_record(i,rec),match.path,field_name))
                # 2.6. delete
                for field_name in self.ns.dname:
                    if field_name in match:
                        match.dirty=True
                        del match[field_name]
                        if not self.ns.quiet:
                            print("merge: DELETE %s[%s]" % (match["key"],field_name), file=sys.stderr)
                # 3. save changes, provided there is not a --new switch
                if not self.ns.new:
                    match.save()
            if record_bounced:
                bounced_records_num+=1
        if bounced_fields_num and not self.ns.quiet:
            print("merge: %d fields in %d records bounced" % (bounced_fields_num,bounced_records_num), file=sys.stderr)
            print(("merge: the field names of the bounced fields are: %s" % ",".join(glob_bounced_fields)), file=sys.stderr)
            if not self.ns.verbose:
                print("merge: Use -v to see identify these fields, use -q to supress this message.", file=sys.stderr)
