from yadata.command import Render
from yadata.record import Record, AddOneToMany, AddManyToMany
from types import SimpleNamespace
import pytest

class ROwner(Record):

    yadata_tag='!ROwner'

class RBigOwner(ROwner):

    yadata_tag='!RBigOwner'

@AddOneToMany('owner',ROwner,'pets')
class RPet(Record):

    yadata_tag='!RPet'
    flag: bool

@AddOneToMany('pet',RPet,'toys')
class RToy(Record):

    yadata_tag='!RToy'

class RTag(Record):

    yadata_tag='!RTag'

@AddManyToMany('tags',RTag,'items')
class RItem(Record):

    yadata_tag='!RItem'

def render(tmp_path,template,records,template_name='t.txt',**kwargs):

    (tmp_path/template_name).write_text(template)
    ns=SimpleNamespace(
        extra_yaml=None,
        template_dir=str(tmp_path),
        soft_references=False,
        jinja_prefix=None,
        template=template_name,
    )
    for key,value in kwargs.items():
        setattr(ns,key,value)
    Render(ns).execute(records)

LIST_ALL='''# for rec in records
{{ rec._key }}
# endfor
'''

def test_otm_resolution(tmp_path,capsys):

    ann=ROwner(_key='ann')
    rex=RPet(_key='rex',owner='ann')
    fido=RPet(_key='fido',owner='ann')
    render(tmp_path,'''# for p in records_by_type('ROwner')
{{ p._key }}: {% for x in p.pets %}{{ x._key }} {% endfor %}
# endfor
{{ record_by_tag_and_key('!RPet','rex').owner._key }}
''',[ann,rex,fido])
    assert capsys.readouterr().out=='ann: rex fido \nann'
    assert rex['owner'] is ann

def test_otm_missing_or_none_is_not_dangling(tmp_path,capsys):

    render(tmp_path,LIST_ALL,[RPet(_key='rex'),RPet(_key='fido',owner=None)])
    assert capsys.readouterr().out.split()==['rex','fido']

def test_otm_dangling_raises(tmp_path):

    with pytest.raises(KeyError):
        render(tmp_path,LIST_ALL,[RPet(_key='rex',owner='nobody')])

def test_otm_dangling_soft_cascades(tmp_path,capsys):

    records=[
        ROwner(_key='ann'),
        RPet(_key='rex',owner='nobody'),
        RToy(_key='ball',pet='rex'),
        RPet(_key='fido',owner='ann'),
        RToy(_key='bone',pet='fido'),
    ]
    render(tmp_path,LIST_ALL+'''# for p in records_by_type('ROwner')
pets of {{ p._key }}: {% for x in p.pets %}{{ x._key }} {% endfor %}
# endfor
''',records,soft_references=True)
    out=capsys.readouterr().out
    assert out.split('\n')[:3]==['ann','fido','bone']
    assert 'pets of ann: fido \n' in out

def test_mtm_resolution(tmp_path,capsys):

    a=RTag(_key='a')
    b=RTag(_key='b')
    item=RItem(_key='i',tags=['a','b'])
    render(tmp_path,'''# for t in records_by_type('RTag')
{{ t._key }}: {% for x in t['items'] %}{{ x._key }}{% endfor %}
# endfor
''',[a,b,item])
    assert capsys.readouterr().out=='a: i\nb: i\n'
    assert item['tags']==[a,b]

def test_mtm_dangling(tmp_path,capsys):

    with pytest.raises(KeyError):
        render(tmp_path,LIST_ALL,[RTag(_key='a'),RItem(_key='i',tags=['a','nope'])])
    a=RTag(_key='a')
    item=RItem(_key='i',tags=['a','nope'])
    render(tmp_path,LIST_ALL,[a,item],soft_references=True)
    assert item['tags']==[a]

def test_edge_tags(tmp_path,capsys):

    render(tmp_path,'''{{ edge_tags[('owner','rex','ann')] }}
{{ edge_tags[('pets','ann','rex')] }}
{{ edge_tags[('tags','i','a')] }}
''',[
        ROwner(_key='ann'),
        RPet(_key='rex',owner='ann;friend, old'),
        RTag(_key='a'),
        RItem(_key='i',tags=['a;x']),
    ])
    assert capsys.readouterr().out.split('\n')==["['friend', 'old']","['friend', 'old']","['x']"]

def test_records_by_type_includes_subclasses(tmp_path,capsys):

    render(tmp_path,'''{% for r in records_by_type('ROwner') %}{{ r._key }} {% endfor %}''',
        [ROwner(_key='ann'),RBigOwner(_key='big'),RTag(_key='a')])
    assert capsys.readouterr().out=='ann big '

def test_field_input_escapes(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(records[0],'note') }}''',[RPet(_key='rex',note='<b>&"')])
    out=capsys.readouterr().out
    assert 'name="RPet;rex;note"' in out
    assert '<b>' not in out
    assert '&lt;b&gt;&amp;' in out

def test_field_input_bool(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(records[0],'flag') }}''',[RPet(_key='rex',flag=False)])
    out=capsys.readouterr().out
    assert out.startswith('<select name="RPet;rex;flag"')
    assert '<option value="false" selected="selected">no</option>' in out
    assert '<option value="true">yes</option>' in out

def test_field_input_otm(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(record_by_tag_and_key('!RPet','rex'),'owner') }}''',
        [ROwner(_key='bob'),ROwner(_key='ann'),RPet(_key='rex',owner='bob')])
    out=capsys.readouterr().out
    options=[line for line in out.split('\n') if line.startswith('<option')]
    assert options==[
        '<option value="null">--</option>',
        '<option value="&quot;ann&quot;">ann</option>',
        '<option value="&quot;bob&quot;" selected="selected">bob</option>',
    ]

@pytest.mark.parametrize('template,given,expected',[
    ('t.txt',None,'#'),
    ('t.md',None,'%%'),
    ('t.md','@','@'),
])
def test_jinja_prefix(template,given,expected):

    ns=SimpleNamespace(extra_yaml=None,template=template,jinja_prefix=given)
    assert Render(ns).ns.jinja_prefix==expected

def test_md_template_uses_percent_prefix(tmp_path,capsys):

    render(tmp_path,'''%% for rec in records
* {{ rec._key }}
%% endfor
# heading
''',[ROwner(_key='ann')],template_name='t.md')
    assert capsys.readouterr().out=='* ann\n# heading'

def test_extra_yaml(tmp_path,capsys):

    render(tmp_path,'{{ extra.a }}',[],extra_yaml=None)
    capsys.readouterr()
    ns=SimpleNamespace(extra_yaml='{a: 42}',template='t.txt',jinja_prefix=None,
        template_dir=str(tmp_path),soft_references=False)
    Render(ns).execute([])
    assert capsys.readouterr().out=='42'

def test_sort_by_filter(tmp_path,capsys):

    render(tmp_path,'''{% for r in records|sort_by('~n','_key') %}{{ r._key }} {% endfor %}''',
        [RTag(_key='a',n=1),RTag(_key='c',n=2),RTag(_key='b',n=2)])
    assert capsys.readouterr().out=='b c a '

def test_non_string_keys(tmp_path,capsys):

    owner=ROwner(_key=1)
    tag=RTag(_key=2)
    pet=RPet(_key='rex',owner=1)
    item=RItem(_key='i',tags=[2])
    render(tmp_path,LIST_ALL,[owner,tag,pet,item])
    assert pet['owner'] is owner
    assert item['tags']==[tag]

def test_field_input_text_and_number(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(records[0],'note') }}
{{ field_input(records[0],'note',textarea=True) }}
{{ field_input(records[0],'n') }}''',[RPet(_key='rex',note='hi',n=3)])
    assert capsys.readouterr().out.split('\n')==[
        '<input type="text" name="RPet;rex;note" id="RPet;rex;note" value="hi" autocomplete="off">',
        '<textarea name="RPet;rex;note" id="RPet;rex;note" rows="6" cols="33" autocomplete="off">',
        'hi',
        '</textarea>',
        '<input type="text" name="RPet;rex;n" id="RPet;rex;n" value="3" autocomplete="off">',
    ]

def test_field_input_otm_none(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(records[1],'owner') }}''',[ROwner(_key='ann'),RPet(_key='rex',owner=None)])
    assert '<option value="null" selected="selected">--</option>' in capsys.readouterr().out

def test_time_now(tmp_path,capsys):

    import datetime
    render(tmp_path,'{{ time_now.year }}',[])
    assert capsys.readouterr().out==str(datetime.datetime.now().year)

def test_missing_template(tmp_path):

    import jinja2
    ns=SimpleNamespace(extra_yaml=None,template_dir=str(tmp_path),soft_references=False,
        jinja_prefix=None,template='nope.txt')
    with pytest.raises(jinja2.TemplateNotFound):
        Render(ns).execute([])

def test_field_input_otm_int_keys(tmp_path,capsys):

    render(tmp_path,'''{{ field_input(record_by_tag_and_key('!RPet','rex'),'owner') }}''',
        [ROwner(_key=2),ROwner(_key=1),RPet(_key='rex',owner=1)])
    options=[line for line in capsys.readouterr().out.split('\n') if line.startswith('<option')]
    assert options==[
        '<option value="null">--</option>',
        '<option value="1" selected="selected">1</option>',
        '<option value="2">2</option>',
    ]
