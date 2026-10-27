from yadata.record import Record
from yadata.utils.misc import unique, describe_record
import yadata.utils.sane_yaml as sane_yaml

class YamlRecord(Record):

    yadata_tag='!YamlRecord'
    top_fields=['title','year']

def test_dump_field_order():

    rec=YamlRecord(z=1,year=2000,_key='k',a=2,title='T')
    assert sane_yaml.dump(rec)=='!YamlRecord\n_key: k\ntitle: T\nyear: 2000\nz: 1\na: 2\n'

def test_dump_plain_dict():

    assert sane_yaml.dump({'b':1,'_key':'k'})=='_key: k\nb: 1\n'

def test_dump_unicode():

    assert sane_yaml.dump(YamlRecord(name='Gejza Jenča'))=='!YamlRecord\nname: Gejza Jenča\n'

def test_dump_lists_flow_style():

    assert sane_yaml.dump(YamlRecord(tags=['a','b']))=='!YamlRecord\ntags: [a, b]\n'

def test_round_trip():

    rec=YamlRecord(_key='k',title='Ťava',tags=['a'],nested={'x':[1,2]},n=1.5,flag=True,none=None)
    back=list(sane_yaml.load_all('---\n'+sane_yaml.dump(rec)))
    assert back==[rec]
    assert type(back[0]) is YamlRecord

def test_unique():

    assert unique([3,1,3,2,1])==[3,1,2]
    assert unique([{'a':1},{'a':1},{'b':2}])==[{'a':1},{'b':2}]
    assert unique([])==[]

def test_describe_record():

    assert describe_record(3,{'_key':'k'})=='record no. 3 (_key=k)'
    assert describe_record(0,{})=='record no. 0 (_key=None)'

def test_yadata_log(monkeypatch,capsys):

    from yadata.utils.misc import _yadata_log
    monkeypatch.delenv('YADATA_DEBUG',raising=False)
    _yadata_log('quiet')
    monkeypatch.setenv('YADATA_DEBUG','1')
    _yadata_log('loud',1)
    assert capsys.readouterr().err=='loud 1\n'

def test_load_is_safe_load():

    assert sane_yaml.load('{a: [1, x]}')=={'a':[1,'x']}

def test_load_all_plain_and_tagged():

    docs=list(sane_yaml.load_all('--- {a: 1}\n--- !YamlRecord {b: 2}\n--- 3\n'))
    assert docs==[{'a':1},YamlRecord(b=2),3]
    assert type(docs[1]) is YamlRecord
