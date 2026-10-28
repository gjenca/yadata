from yadata.command import Exec
from yadata.record import Record
from collections import namedtuple
import pytest

class TryRecord(Record):

    yadata_tag='!TryRecord'

    def is_my_type(cls,d):
        return True

MockExecNameSpace=namedtuple('MockExecNameSpace',['statement','no_output','failed','restrict','keep_going','module','type'],defaults=[None])

def test_exec_yes_output():
    
    t_in=TryRecord(fieldname=["a","b","c"])
    t_should_out=TryRecord(fieldname=["a","b","c","d"])
    ns=MockExecNameSpace(
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
    ns=MockExecNameSpace(
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
    ns=MockExecNameSpace(
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
    
    ns=MockExecNameSpace(
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
    
    ns=MockExecNameSpace(
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
    
    ns=MockExecNameSpace(
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

class OtherRecord(Record):

    yadata_tag='!ExecOtherRecord'

class TypedRecord(Record):

    yadata_tag='!ExecTypedRecord'
    n: int

def exec_ns(statement,**kwargs):

    fields=dict(statement=statement,no_output=False,failed=False,restrict='',keep_going=False,module=[])
    fields.update(kwargs)
    return MockExecNameSpace(**fields)

def test_exec_type():

    t_in=[TryRecord(n=1),OtherRecord(n=1)]
    out=list(Exec(exec_ns('n+=1',type='TryRecord')).execute(t_in))
    assert out==[TryRecord(n=2),OtherRecord(n=1)]

def test_exec_restrict_type_variable():

    t_in=[TryRecord(n=1),OtherRecord(n=1)]
    out=list(Exec(exec_ns('n+=1',restrict='_type=="OtherRecord"')).execute(t_in))
    assert out==[TryRecord(n=1),OtherRecord(n=2)]

def test_exec_restrict_error_raises():

    with pytest.raises(NameError):
        list(Exec(exec_ns('n=1',restrict='missing')).execute([TryRecord()]))

def test_exec_restrict_error_keep_going(capsys):

    t_in=[TryRecord(n=1),TryRecord(n=2,flag=True)]
    out=list(Exec(exec_ns('n+=1',restrict='flag',keep_going=True)).execute(t_in))
    assert out==[TryRecord(n=1),TryRecord(n=3,flag=True)]
    err=capsys.readouterr().err
    assert 'exec: Warning: failed on record no. 0' in err
    assert 'there were 1 exceptions' in err

def test_exec_restrict_error_failed():

    t_in=[TryRecord(n=1),TryRecord(n=2,flag=True)]
    out=list(Exec(exec_ns('n+=1',restrict='flag',failed=True)).execute(t_in))
    assert out==[TryRecord(n=1)]

def test_exec_assignment_is_type_checked():

    import typeguard
    with pytest.raises(TypeError):
        list(Exec(exec_ns('n="x"')).execute([TypedRecord(n=1)]))

def test_exec_new_field():

    out=list(Exec(exec_ns('m=n*2')).execute([TryRecord(n=2)]))
    assert out==[TryRecord(n=2,m=4)]
