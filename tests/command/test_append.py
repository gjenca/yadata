from yadata.command import Append
from yadata.record import Record
import pytest

class TryRecord(Record):

    yadata_tag='!TryRecord'

    def is_my_type(cls,d):
        return True

class NameSpace(object):

    pass


def test_append_existent():

    t_in=TryRecord(fieldname=["a","b","c"])
    t_should_out=TryRecord(fieldname=["a","b","c","d"])
    ns=NameSpace()
    ns.fieldname='fieldname'
    ns.string='d'
    append_command=Append(ns)
    iter_out=append_command.execute([t_in])
    t_out=next(iter_out)
    assert set(t_out['fieldname'])==set(t_should_out['fieldname'])
    assert len(t_out)==len(t_should_out)
    with pytest.raises(StopIteration):
        next(iter_out)

def test_append_nonexistent():

    t_in=TryRecord(fieldname=["a","b","c"])
    t_should_out=TryRecord(fieldname=["a","b","c"],other_fieldname=["d"])
    ns=NameSpace()
    ns.fieldname='other_fieldname'
    ns.string='d'
    append_command=Append(ns)
    iter_out=append_command.execute([t_in])
    t_out=next(iter_out)
    for f in t_in:
        assert set(t_out[f])==set(t_should_out[f])
    assert len(t_out)==len(t_should_out)
    with pytest.raises(StopIteration):
        next(iter_out)
    
def test_append_nonlist():

    t_in=TryRecord(fieldname=1967)
    ns=NameSpace()
    ns.fieldname='fieldname'
    ns.string='d'
    append_command=Append(ns)
    with pytest.raises(TypeError):
        iter_out=append_command.execute([t_in])
        t_out=next(iter_out)
    

def test_append_keeps_order_and_dedupes():

    ns=NameSpace()
    ns.fieldname='fieldname'
    ns.string=['c','a','d','d']
    out=list(Append(ns).execute([TryRecord(fieldname=['b','a'])]))
    assert out[0]['fieldname']==['b','a','c','d']

def test_append_multiple_records():

    ns=NameSpace()
    ns.fieldname='f'
    ns.string=['x']
    out=list(Append(ns).execute([TryRecord(f=['a']),TryRecord()]))
    assert [rec['f'] for rec in out]==[['a','x'],['x']]
