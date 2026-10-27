from yadata.command import Filter
from yadata.record import Record
from collections import namedtuple
import pytest

class TryRecord(Record):

    yadata_tag='!TryRecord'

    def is_my_type(cls,d):
        return True

MockFilterNameSpace=namedtuple('MockFilterNameSpace',['expr','failed','module','keep_going','type'])

def test_filter_normal():
    
    t_in_1=TryRecord(fieldname=['a','b','c'])
    t_in_2=TryRecord(fieldname=['x','y','z'])
    t_in_3=TryRecord(fieldname=['x','y','a'])
    t_should_out_1=t_in_1
    t_should_out_2=t_in_3
    ns=MockFilterNameSpace(
        expr='"a" in fieldname',
        failed=False,
        module=[],
        keep_going=False,
        type=None,
    )
    exec_command=Filter(ns)
    iter_out=exec_command.execute([t_in_1,t_in_2,t_in_3])
    assert list(iter_out)==[t_should_out_1,t_should_out_2]

def test_filter_module():
    
    t_in_1=TryRecord(number=10.1)
    t_in_2=TryRecord(number=9.1)
    t_in_3=TryRecord(number=11.2)
    t_should_out_1=t_in_1
    t_should_out_2=t_in_3
    ns=MockFilterNameSpace(
        expr='math.floor(number)>9',
        failed=False,
        module=['math'],
        keep_going=False,
        type=None,
    )
    exec_command=Filter(ns)
    iter_out=exec_command.execute([t_in_1,t_in_2,t_in_3])
    assert list(iter_out)==[t_should_out_1,t_should_out_2]

def test_filter_failed():
    
    t_in_1=TryRecord(numberr=10.1)
    t_in_2=TryRecord(number=9.1)
    t_in_3=TryRecord(number=11.2)
    t_should_out_1=t_in_2
    t_should_out_2=t_in_3
    ns=MockFilterNameSpace(
        expr='numberr==0',
        failed=True,
        module=[],
        keep_going=False,
        type=None,

    )
    exec_command=Filter(ns)
    iter_out=exec_command.execute([t_in_1,t_in_2,t_in_3])
    assert list(iter_out)==[t_should_out_1,t_should_out_2]

def test_filter_keep_going():
    
    t_in_1=TryRecord(numberr=10.1)
    t_in_2=TryRecord(number=9.1)
    t_in_3=TryRecord(numberr=11.2)
    t_should_out_1=t_in_1
    t_should_out_2=t_in_3
    ns=MockFilterNameSpace(
        expr='numberr>10',
        failed=False,
        module=[],
        keep_going=True,
        type=None,
    )
    exec_command=Filter(ns)
    iter_out=exec_command.execute([t_in_1,t_in_2,t_in_3])
    assert list(iter_out)==[t_should_out_1,t_should_out_2]


class OtherRecord(Record):

    yadata_tag='!FilterOtherRecord'

def test_filter_type():

    t_in=[TryRecord(n=1),OtherRecord(n=1),TryRecord(n=2)]
    ns=MockFilterNameSpace(expr='n>1',failed=False,module=[],keep_going=False,type='TryRecord')
    assert list(Filter(ns).execute(t_in))==[OtherRecord(n=1),TryRecord(n=2)]

def test_filter_type_variable():

    t_in=[TryRecord(n=1),OtherRecord(n=1)]
    ns=MockFilterNameSpace(expr='_type=="OtherRecord"',failed=False,module=[],keep_going=False,type=None)
    assert list(Filter(ns).execute(t_in))==[OtherRecord(n=1)]

def test_filter_error_raises():

    ns=MockFilterNameSpace(expr='missing',failed=False,module=[],keep_going=False,type=None)
    with pytest.raises(NameError):
        list(Filter(ns).execute([TryRecord()]))

def test_filter_keep_going_message(capsys):

    ns=MockFilterNameSpace(expr='missing',failed=False,module=[],keep_going=True,type=None)
    assert list(Filter(ns).execute([TryRecord(_key='k')]))==[]
    err=capsys.readouterr().err
    assert 'filter: Warning: failed on record no. 0 (_key=k)' in err
    assert 'filter: Warning: there were 1 exceptions' in err

def test_filter_does_not_modify_records():

    rec=TryRecord(n=1)
    ns=MockFilterNameSpace(expr='n==1',failed=False,module=[],keep_going=False,type=None)
    assert list(Filter(ns).execute([rec]))==[rec]
    assert rec==TryRecord(n=1)
