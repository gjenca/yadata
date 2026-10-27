from yadata.record import Record, AddOneToMany
from yadata.datadir import Datadir
import yadata.utils.sane_yaml as sane_yaml
import pytest
import yaml
import typeguard

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

# key generation

class PrefixRecord(Record):

    yadata_tag='!PrefixRecord'
    key_format='{name}'

    def get_key_prefix(self):
        return 'p-'+self['name']

class KeylessRecord(Record):

    yadata_tag='!KeylessRecord'

def test_key_format():

    assert MergeRecord(name='x').key()=='x'

def test_key_prefix_wins():

    assert PrefixRecord(name='x').key()=='p-x'

def test_no_key_method():

    with pytest.raises(TypeError):
        KeylessRecord(name='x').key()

def test_generated_keys_avoid_collisions(tmp_path):

    dd=Datadir(str(tmp_path))
    for year in (1,2,3):
        dd.merge(MergeRecord(name='x',year=year),{})
    assert sorted(dd.keys)==['x','x_0','x_1']
    assert sorted(p.name for p in tmp_path.iterdir())==['x.yaml','x_0.yaml','x_1.yaml']

# field access and type checks

def test_dotted_key():

    # Dotted keys traverse nested Records; nested plain dicts are not supported
    rec=MergeRecord(a=MergeRecord(b=MergeRecord(c=1)))
    assert rec['a.b.c']==1
    assert rec['a.b']==MergeRecord(c=1)

def test_setitem_type_check():

    rec=MergeRecord(tags=['a'])
    with pytest.raises(typeguard.TypeCheckError):
        rec['tags']=[1]
    assert rec['tags']==['a']

def test_init_type_check():

    with pytest.raises(TypeError):
        MergeRecord(tags=[1])

def test_dirty(tmp_path):

    (tmp_path/'x.yaml').write_text('!MergeRecord {_key: x, name: x}\n')
    dd=Datadir(str(tmp_path))
    rec=dd.keys['x']
    assert not rec.dirty
    before=(tmp_path/'x.yaml').stat().st_mtime_ns
    rec.save(dd)
    assert (tmp_path/'x.yaml').stat().st_mtime_ns==before
    rec['year']=1
    assert rec.dirty

def test_merge_extend():

    rec=MergeRecord(_key='x',name='x',tags=['a'])
    rec.dirty=False
    bounced,log=rec.merge(MergeRecord(name='x',tags=['a','b']),{'tags':'extend'})
    assert rec['tags']==['a','a','b']
    assert rec.dirty
    assert (log[0].oldvalue,log[0].newvalue)==(['a'],['a','a','b'])

def test_merge_extend_is_saved(tmp_path):

    (tmp_path/'x.yaml').write_text('!MergeRecord {_key: x, name: x, tags: [a]}\n')
    Datadir(str(tmp_path)).merge(MergeRecord(_key='x',tags=['b']),{'tags':'extend'})
    assert Datadir(str(tmp_path)).keys['x']['tags']==['a','b']

# Datadir

def test_list_matching(tmp_path):

    (tmp_path/'x.yaml').write_text('!MergeRecord {_key: x, name: x}\n')
    dd=Datadir(str(tmp_path))
    assert dd.list_matching(MergeRecord(_key='x',name='other'))==[dd.keys['x']]
    assert dd.list_matching(MergeRecord(_key='y',name='x'))==[]
    assert dd.list_matching(MergeRecord(name='x'))==[]

def test_keyless_record_rejected(tmp_path):

    (tmp_path/'a.yaml').write_text('!MergeRecord {_key: a, name: a}\n')
    (tmp_path/'b.yaml').write_text('!MergeRecord {name: z}\n')
    with pytest.raises(ValueError,match='b.yaml contains a record without _key'):
        Datadir(str(tmp_path))

def test_non_record_file(tmp_path):

    (tmp_path/'a.yaml').write_text('{name: z}\n')
    with pytest.raises(TypeError):
        Datadir(str(tmp_path))

def test_tmp_files_ignored(tmp_path):

    (tmp_path/'a.yaml').write_text('!MergeRecord {_key: a, name: a}\n')
    (tmp_path/'tmpabc.tmp').write_text('!MergeRecord {_key: a, name: half-written\n')
    assert list(Datadir(str(tmp_path)).keys)==['a']

# relationships

class RelOwner(Record):

    yadata_tag='!RelOwner'

@AddOneToMany('owner',RelOwner,'pets')
class RelPet(Record):

    yadata_tag='!RelPet'

def test_inverse_fields():

    owner=RelOwner(_key='ann')
    assert owner['pets']==[]
    owner['pets'].append(RelPet(_key='rex'))
    assert 'pets' not in repr(owner)
    assert 'pets' not in sane_yaml.dump(owner)
    assert RelOwner._inverse==['pets']
    assert RelPet._one_to_many[0].inverse_type is RelOwner

# tags, logging, serialization

class AutoTagged(Record):

    yadata_tag='auto'

class Untagged(Record):

    pass

def test_auto_tag():

    assert AutoTagged.yadata_tag=='!AutoTagged'
    assert list(sane_yaml.load_all('--- !AutoTagged {a: 1}\n'))==[AutoTagged(a=1)]

def test_untagged_class_has_no_tag():

    assert not hasattr(Untagged,'yadata_tag')

def test_log_entry_repr():

    rec=MergeRecord(_key='x',name='x',year=1)
    _,log=rec.merge(MergeRecord(name='x',year=2,new=3),{'year':'set'})
    assert [repr(entry) for entry in log]==[
        '_key=x[year] 1->2 (method:set)',
        '_key=x[new] None->3 (method:new-field)',
    ]

def test_merge_into_keyless_record():

    with pytest.raises(ValueError,match='without key'):
        MergeRecord(name='x').merge(MergeRecord(name='x'),{})

def test_merge_first_matching_pattern_wins():

    rec=MergeRecord(_key='x',name='x',tags=['a'])
    rec.merge(MergeRecord(name='x',tags=['b']),{'t*':'union','tags':'set'})
    assert rec['tags']==['a','b']

def test_bounce_omits_inverse_fields():

    owner=RelOwner(_key='ann',age=1)
    bounced,_=owner.merge(RelOwner(age=2),{})
    assert dict(bounced)=={'_key':'ann','age':2}

def test_to_yaml_and_stream_out():

    import io
    rec=MergeRecord(_key='x',name='x')
    assert rec.to_yaml()=='!MergeRecord\n_key: x\nname: x\n'
    f=io.StringIO()
    rec.stream_out(f)
    assert f.getvalue()=='---\n!MergeRecord\n_key: x\nname: x\n'

def test_key_format_missing_field():

    with pytest.raises(KeyError):
        MergeRecord(year=1).key()

def test_save_into_subdir(tmp_path):

    class SubdirRecord(Record):
        yadata_tag='!SubdirRecord'
        key_format='{name}'
        subdir='a/b'
    dd=Datadir(str(tmp_path))
    dd.merge(SubdirRecord(name='x'),{})
    assert (tmp_path/'a'/'b'/'x.yaml').read_text()=='!SubdirRecord\n_key: x\nname: x\n'

def test_deprecated_sort_arguments_warn(capsys):

    from yadata.record import AddManyToMany
    class W1(Record):
        pass
    @AddManyToMany('w1s',W1,'w2s',sort_by='x')
    class W2(Record):
        pass
    @AddOneToMany('w1',W1,'w3s',inverse_sort_by='x')
    class W3(Record):
        pass
    err=capsys.readouterr().err
    assert 'W2: sort_by and inverse_sort_by are deprecated' in err
    assert 'W3: inverse_sort_by is deprecated' in err
    assert W2._many_to_many[0].sort_by is None
