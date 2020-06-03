from yadata.command import Exec
from yadata.record import Record
from collections import namedtuple
import pytest

class TryRecord(Record):

    yadata_tag='!TryRecord'

    def is_my_type(cls,d):
        return True

MockNameSpace=namedtuple('MockNameSpace',['statement','no_output','failed','restrict','keep_going','module'])

def test_exec_yes_output():
    
    t_in=TryRecord(fieldname=["a","b","c"])
    t_should_out=TryRecord(fieldname=["a","b","c","d"])
    ns=MockNameSpace(
        statement='fieldname.append("d")',
        no_output=False,
        failed=False,
        restrict='',
        keep_going=False,
        module=[]
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in])
    t_out=next(iter_out)
    assert t_out['fieldname']==t_should_out['fieldname']
    assert len(t_out)==len(t_should_out)
    with pytest.raises(StopIteration):
        next(iter_out)

def test_exec_no_output():
    
    t_in=TryRecord(fieldname=["a","b","c"])
    ns=MockNameSpace(
        statement='fieldname.append("d")',
        no_output=True,
        failed=False,
        restrict='',
        keep_going=False,
        module=[]
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in])
    with pytest.raises(StopIteration):
        next(iter_out)

def test_exec_failed():
    
    t_in=TryRecord(fieldname="bumbac")
    t_should_out=TryRecord(fieldname="bumbac")
    ns=MockNameSpace(
        statement='fieldname.append("d")',
        no_output=False,
        failed=True,
        restrict='',
        keep_going=False,
        module=[]
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in])
    t_out=next(iter_out)
    assert t_out['fieldname']==t_should_out['fieldname']
    assert len(t_out)==len(t_should_out)
    with pytest.raises(StopIteration):
        next(iter_out)

def test_exec_restrict():
    
    t_in_yes=TryRecord(fieldname=["a","b","c"],ignore=False)
    t_in_no=TryRecord(fieldname=["x","y","z"],ignore=True)
    t_should_out_yes=TryRecord(fieldname=["a","b","c","d"],ignore=False)
    t_should_out_no=TryRecord(fieldname=["x","y","z"],ignore=True)
    
    ns=MockNameSpace(
        statement='fieldname.append("d")',
        no_output=False,
        failed=False,
        restrict='not ignore',
        keep_going=False,
        module=[]
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in_yes,t_in_no])
    assert list(iter_out)==[t_should_out_yes,t_should_out_no]

def test_exec_keep_going():

    
    t_in_yes=TryRecord(fieldname="bumbac")
    t_in_no=TryRecord(fieldname=["x","y","z"])
    t_should_out_yes=TryRecord(fieldname="bumbac")
    t_should_out_no=TryRecord(fieldname=["x","y","z","d"])
    
    ns=MockNameSpace(
        statement='fieldname.append("d")',
        no_output=False,
        failed=False,
        restrict='',
        keep_going=True,
        module=[]
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in_yes,t_in_no])
    assert list(iter_out)==[t_should_out_yes,t_should_out_no]

def test_exec_module():

    
    t_in_yes=TryRecord(x=10.1)
    t_in_no=TryRecord(x=11.1)
    t_should_out_yes=TryRecord(x=10,y=11)
    t_should_out_no=TryRecord(x=11,y=12)
    
    ns=MockNameSpace(
        statement='y=math.ceil(x);x=math.floor(x)',
        no_output=False,
        failed=False,
        restrict='',
        keep_going=True,
        module=['math']
    )
    exec_command=Exec(ns)
    iter_out=exec_command.execute([t_in_yes,t_in_no])
    assert list(iter_out)==[t_should_out_yes,t_should_out_no]
