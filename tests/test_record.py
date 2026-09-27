from yadata.record import Record
from yadata.datadir import Datadir
import yadata.utils.sane_yaml as sane_yaml
import pytest
import yaml

class MergeRecord(Record):

    yadata_tag='!MergeRecord'
    key_format='{name}'
    tags: list[str]

def test_merge_new_field():

    rec=MergeRecord(_key='x',name='x')
    bounced,log=rec.merge(MergeRecord(name='x',year=2000),{})
    assert bounced=={}
    assert rec['year']==2000
    assert [entry.method for entry in log]==['new-field']

def test_merge_equal_field():

    rec=MergeRecord(_key='x',name='x')
    bounced,log=rec.merge(MergeRecord(name='x'),{})
    assert bounced=={}
    assert log==[]

def test_merge_bounce():

    rec=MergeRecord(_key='x',name='x',year=2000)
    bounced,log=rec.merge(MergeRecord(name='x',year=2001),{})
    assert rec['year']==2000
    assert type(bounced) is MergeRecord
    assert dict(bounced)=={'_key':'x','year':2001}

def test_merge_set():

    rec=MergeRecord(_key='x',name='x',year=2000)
    bounced,log=rec.merge(MergeRecord(name='x',year=2001),{'year':'set'})
    assert bounced=={}
    assert rec['year']==2001

def test_merge_union_keeps_order():

    rec=MergeRecord(_key='x',name='x',tags=['b','a'])
    bounced,log=rec.merge(MergeRecord(name='x',tags=['a','c']),{'tags':'union'})
    assert bounced=={}
    assert rec['tags']==['b','a','c']

def test_merge_glob():

    rec=MergeRecord(_key='x',name='x',year_from=2000,year_to=2001,title='a')
    bounced,log=rec.merge(
        MergeRecord(name='x',year_from=1990,year_to=1991,title='b'),
        {'year_*':'set'})
    assert rec['year_from']==1990
    assert rec['year_to']==1991
    assert dict(bounced)=={'_key':'x','title':'b'}

def test_load_checks_nested_types():

    with pytest.raises(TypeError):
        list(sane_yaml.load_all('--- !MergeRecord {name: x, tags: [1, 2]}\n'))

def test_load_is_safe():

    with pytest.raises(yaml.constructor.ConstructorError):
        list(sane_yaml.load_all('--- !!python/object/apply:os.getpid []\n'))

def test_save_and_reload(tmp_path):

    dd=Datadir(str(tmp_path))
    dd.merge(MergeRecord(name='x',tags=['a']),{})
    assert (tmp_path/'x.yaml').exists()
    assert list(tmp_path.iterdir())==[tmp_path/'x.yaml']
    dd2=Datadir(str(tmp_path))
    assert dd2.keys['x']['tags']==['a']

def test_duplicate_keys(tmp_path):

    (tmp_path/'a.yaml').write_text('!MergeRecord {_key: x, name: x}\n')
    (tmp_path/'b.yaml').write_text('!MergeRecord {_key: x, name: y}\n')
    with pytest.raises(ValueError):
        Datadir(str(tmp_path))
