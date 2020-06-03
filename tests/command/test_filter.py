from yadata.command import Filter
from yadata.record import Record
from collections import namedtuple
import pytest

class TryRecord(Record):

    yadata_tag='!TryRecord'

    def is_my_type(cls,d):
        return True

MockFilterNameSpace=namedtuple('MockFilterNameSpace',['expr','failed','module','keep_going'])

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
        keep_going=False
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
        keep_going=False
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
        keep_going=False
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
        keep_going=True
    )
    exec_command=Filter(ns)
    iter_out=exec_command.execute([t_in_1,t_in_2,t_in_3])
    assert list(iter_out)==[t_should_out_1,t_should_out_2]

