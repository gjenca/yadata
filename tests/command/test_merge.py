from yadata.command import Merge
from yadata.datadir import Datadir
from yadata.record import Record
from types import SimpleNamespace
import pytest

class MRec(Record):

    yadata_tag='!MRec'
    key_format='{name}'

def merge(datadir,records,**kwargs):

    ns=SimpleNamespace(datadir=str(datadir),uname=[],sname=[],old=False,new=False,
        verbose=False,quiet=False,bounced=False)
    for key,value in kwargs.items():
        setattr(ns,key,value)
    return list(Merge(ns).execute(records))

@pytest.fixture
def dd(tmp_path):
    """datadir with ann (year 1, tags [a]) and bob"""

    (tmp_path/'ann.yaml').write_text('!MRec {_key: ann, name: ann, year: 1, tags: [a]}\n')
    (tmp_path/'bob.yaml').write_text('!MRec {_key: bob, name: bob}\n')
    return tmp_path

def test_merge_new_records(tmp_path):

    assert merge(tmp_path,[MRec(name='ann'),MRec(name='bob')])==[]
    assert sorted(Datadir(str(tmp_path)).keys)==['ann','bob']

def test_merge_new_field(dd):

    merge(dd,[MRec(_key='bob',name='bob',year=5)])
    assert Datadir(str(dd)).keys['bob']['year']==5

def test_merge_summary(dd,capsys):

    merge(dd,[MRec(_key='ann',name='ann',year=2,tags=['b']),MRec(_key='bob',name='bob')])
    err=capsys.readouterr().err
    assert err.startswith('2 fields in 1 records bounced\n')
    assert Datadir(str(dd)).keys['ann']['year']==1

def test_merge_quiet(dd,capsys):

    merge(dd,[MRec(_key='ann',name='ann',year=2)],quiet=True)
    assert capsys.readouterr().err==''

def test_merge_verbose(dd,capsys):

    merge(dd,[MRec(_key='ann',name='ann',year=2,x=1)],verbose=True)
    err=capsys.readouterr().err.split('\n')
    assert "merge: fields ['year'] in record number 0[ann] bounced" in err
    assert '_key=ann[x] None->1 (method:new-field)' in err

def test_merge_bounced_stream(dd,capsys):

    out=merge(dd,[MRec(_key='ann',name='ann',year=2,x=1),MRec(_key='bob',name='bob')],bounced=True)
    assert out==[MRec(_key='ann',year=2)]
    assert type(out[0]) is MRec
    assert capsys.readouterr().err==''
    assert Datadir(str(dd)).keys['ann']['x']==1

def test_merge_set_and_union(dd):

    merge(dd,[MRec(_key='ann',name='ann',year=2,tags=['b','a'])],sname=['year'],uname=['tags'])
    ann=Datadir(str(dd)).keys['ann']
    assert ann['year']==2
    assert ann['tags']==['a','b']

def test_merge_duplicate_options(dd):

    with pytest.raises(ValueError,match='duplicite'):
        merge(dd,[],sname=['year'],uname=['year'])

def test_merge_old_new(dd):

    records=[MRec(_key='ann',name='ann'),MRec(name='carl')]
    assert merge(dd,records,old=True)==[records[0]]
    assert merge(dd,records,new=True)==[records[1]]
    assert sorted(p.name for p in dd.iterdir())==['ann.yaml','bob.yaml']

def test_merge_requires_records(dd,capsys):

    with pytest.raises(SystemExit) as e:
        merge(dd,[{'name':'ann'}])
    assert e.value.code==1
    assert 'yadata cast' in capsys.readouterr().err

def test_merge_missing_datadir(tmp_path):

    with pytest.raises(NotADirectoryError):
        merge(tmp_path/'nope',[])

def test_merge_keeps_file_location(tmp_path):

    (tmp_path/'deep'/'er').mkdir(parents=True)
    (tmp_path/'deep'/'er'/'ann.yaml').write_text('!MRec {_key: ann, name: ann}\n')
    merge(tmp_path,[MRec(_key='ann',name='ann',year=3)])
    assert [str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*.yaml')]==['deep/er/ann.yaml']
    assert 'year: 3' in (tmp_path/'deep'/'er'/'ann.yaml').read_text()
