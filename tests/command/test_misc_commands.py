from yadata.command import Yield, Type, Cast, Read, Run
import yadata.command.cast
from yadata.record import Record
from types import SimpleNamespace, ModuleType
import sys
import pytest

class MiscRec(Record):

    yadata_tag='!MiscRec'

class MiscSubRec(MiscRec):

    yadata_tag='!MiscSubRec'

class MiscOther(Record):

    yadata_tag='!MiscOther'

@pytest.fixture
def yadata_types(monkeypatch):
    """a fake _yadata_types module with the types defined above"""

    mod=ModuleType('_yadata_types')
    mod.MiscRec=MiscRec
    mod.MiscSubRec=MiscSubRec
    mod.MiscOther=MiscOther
    monkeypatch.setitem(sys.modules,'_yadata_types',mod)
    monkeypatch.setattr(yadata.command.cast,'_yadata_types',mod,raising=False)
    return mod

# yield

def yield_(records,term,generator=False,module=()):

    ns=SimpleNamespace(term=term,generator=generator,module=list(module))
    return list(Yield(ns).execute(records))

def test_yield_term():

    assert yield_([MiscRec(a=1),MiscRec(a=2)],'self["a"]*10')==[10,20]

def test_yield_type():

    assert yield_([MiscRec(),MiscOther()],'_type')==['MiscRec','MiscOther']

def test_yield_generator():

    assert yield_([MiscRec(l=[1,2]),MiscRec(l=[3])],'(x for x in self["l"])',generator=True)==[1,2,3]

def test_yield_module():

    assert yield_([MiscRec(a=4)],'math.sqrt(self["a"])',module=['math'])==[2.0]

def test_yield_exception_propagates():

    with pytest.raises(KeyError):
        yield_([MiscRec()],'self["missing"]')

# type

def type_(records,types,keep_untyped=False):

    ns=SimpleNamespace(types=types,keep_untyped=keep_untyped)
    return list(Type(ns).execute(records))

def test_type_keeps_subclasses(yadata_types):

    records=[MiscRec(_key='r'),MiscSubRec(_key='s'),MiscOther(_key='o'),{'_key':'d'}]
    assert [rec['_key'] for rec in type_(records,['MiscRec'])]==['r','s']
    assert [rec['_key'] for rec in type_(records,['MiscSubRec','MiscOther'])]==['s','o']

def test_type_keep_untyped(yadata_types):

    records=[MiscRec(_key='r'),MiscOther(_key='o'),{'_key':'d'}]
    assert [rec['_key'] for rec in type_(records,['MiscOther'],keep_untyped=True)]==['o','d']

# cast

def test_cast(yadata_types):

    out=list(Cast(SimpleNamespace(type='MiscRec')).execute([{'a':1}]))
    assert type(out[0]) is MiscRec
    assert out[0]=={'a':1}

def test_cast_unknown_type(yadata_types):

    with pytest.raises(AttributeError,match='no type Nope'):
        list(Cast(SimpleNamespace(type='Nope')).execute([{'a':1}]))

def test_cast_no_types_module(monkeypatch):

    monkeypatch.delattr(yadata.command.cast,'_yadata_types',raising=False)
    with pytest.raises(ModuleNotFoundError):
        list(Cast(SimpleNamespace(type='MiscRec')).execute([{'a':1}]))

# read

def test_read(tmp_path):

    (tmp_path/'sub').mkdir()
    (tmp_path/'a.yaml').write_text('!MiscRec {_key: a}\n')
    (tmp_path/'sub'/'b.yaml').write_text('!MiscOther {_key: b}\n')
    (tmp_path/'ignored.txt').write_text('not yaml: [\n')
    out=list(Read(SimpleNamespace(datadir=str(tmp_path))).execute())
    assert sorted((type(rec).__name__,rec['_key']) for rec in out)==[('MiscOther','b'),('MiscRec','a')]

def test_read_missing_dir(tmp_path):

    with pytest.raises(NotADirectoryError):
        list(Read(SimpleNamespace(datadir=str(tmp_path/'nope'))).execute())

# run

def test_run(tmp_path,monkeypatch):

    monkeypatch.chdir(tmp_path)
    Run(SimpleNamespace(shell_command='echo "$YADATA_name $YADATA_n" >> out.txt')).execute(
        [MiscRec(name='ann',n=1),MiscRec(name='bob',n=2)])
    assert (tmp_path/'out.txt').read_text()=='ann 1\nbob 2\n'
