from yadata.record import Record, YadataOptional
import yadata.utils.sane_yaml as sane_yaml
import pytest

class OptRecord(Record):

    yadata_tag='!OptRecord'
    year: YadataOptional[int]
    tags: YadataOptional[list[str]]

def test_init_accepts_value_and_dashes():

    assert OptRecord(year=2000)['year']==2000
    assert OptRecord(year='--')['year']=='--'

def test_setitem_accepts_value_and_dashes():

    rec=OptRecord(year=2000)
    rec['year']='--'
    assert rec['year']=='--'
    rec['year']=2001
    assert rec['year']==2001

def test_init_rejects_other_values():

    with pytest.raises(TypeError):
        OptRecord(year='x')
    with pytest.raises(TypeError):
        OptRecord(year=None)

def test_setitem_rejects_other_values():

    rec=OptRecord(year=2000)
    with pytest.raises(TypeError):
        rec['year']='-'
    assert rec['year']==2000

def test_list_hint():

    assert OptRecord(tags='--')['tags']=='--'
    assert OptRecord(tags=['a'])['tags']==['a']
    with pytest.raises(TypeError):
        OptRecord(tags='a')

def test_error_message():

    with pytest.raises(TypeError,match=r"field 'year' must be int \| Literal\['--'\]"):
        OptRecord(year='x')

def test_load_from_yaml():

    recs=list(sane_yaml.load_all("--- !OptRecord {year: '--'}\n--- !OptRecord\nyear: --\n"))
    assert recs==[OptRecord(year='--'),OptRecord(year='--')]
