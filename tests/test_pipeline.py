import os
import sys
import subprocess
import pytest

REPO_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YADATA_TYPES='''from yadata.record import Record

class Person(Record):

    yadata_tag='auto'
    key_format='{name}'
    subdir='people'
    top_fields=['name']
'''

@pytest.fixture
def yadata(tmp_path):
    """runs the yadata CLI in tmp_path, which contains _yadata_types.py and an empty datadir d"""

    (tmp_path/'_yadata_types.py').write_text(YADATA_TYPES)
    (tmp_path/'d').mkdir()
    env=dict(os.environ,PYTHONPATH=REPO_ROOT)

    def run(*args,stdin=''):
        return subprocess.run(
            [sys.executable,'-c','from yadata.main import run; run()',*args],
            input=stdin,capture_output=True,text=True,cwd=tmp_path,env=env)

    return run

def datadir_files(tmp_path):

    return sorted(str(p.relative_to(tmp_path)) for p in (tmp_path/'d').rglob('*') if p.is_file())

def test_cast_merge_read(yadata,tmp_path):

    r=yadata('cast','Person','!','merge','d',stdin='--- {name: ann, age: 30}\n--- {name: bob}\n')
    assert r.returncode==0,r.stderr
    assert datadir_files(tmp_path)==['d/people/ann.yaml','d/people/bob.yaml']
    r=yadata('read','d','!','sort','-k','name')
    assert r.returncode==0,r.stderr
    assert r.stdout=='---\n!Person\n_key: ann\nname: ann\nage: 30\n---\n!Person\n_key: bob\nname: bob\n'

def test_merge_bounce(yadata,tmp_path):

    yadata('cast','Person','!','merge','d',stdin='--- {name: ann, year: 1}\n')
    changed='--- {_key: ann, name: ann, year: 2}\n'
    r=yadata('cast','Person','!','merge','d',stdin=changed)
    assert r.returncode==0,r.stderr
    assert '1 fields in 1 records bounced' in r.stderr
    r=yadata('cast','Person','!','merge','-b','d',stdin=changed)
    assert r.stdout=='---\n!Person\n_key: ann\nyear: 2\n'
    assert 'year: 1' in (tmp_path/'d/people/ann.yaml').read_text()

def test_merge_set_glob(yadata,tmp_path):

    yadata('cast','Person','!','merge','d',stdin='--- {name: ann, year_a: 1, year_b: 1, x: 1}\n')
    r=yadata('cast','Person','!','merge','-s','year_*','d',stdin='--- {_key: ann, name: ann, year_a: 2, year_b: 3, x: 2}\n')
    assert r.returncode==0,r.stderr
    text=(tmp_path/'d/people/ann.yaml').read_text()
    assert 'year_a: 2' in text
    assert 'year_b: 3' in text
    assert 'x: 1' in text

def test_merge_old_new(yadata,tmp_path):

    yadata('cast','Person','!','merge','d',stdin='--- {name: ann}\n')
    stream='--- {_key: ann, name: ann}\n--- {name: bob}\n'
    r=yadata('cast','Person','!','merge','-o','d',stdin=stream)
    assert r.stdout=='---\n!Person\n_key: ann\nname: ann\n'
    r=yadata('cast','Person','!','merge','-n','d',stdin=stream)
    assert r.stdout=='---\n!Person\nname: bob\n'
    assert datadir_files(tmp_path)==['d/people/ann.yaml']
    r=yadata('cast','Person','!','merge','-o','-n','d',stdin=stream)
    assert r.returncode==2
    assert 'not allowed with' in r.stderr

def test_merge_requires_cast(yadata):

    r=yadata('merge','d',stdin='--- {name: ann}\n')
    assert r.returncode==1
    assert 'yadata cast' in r.stderr

def test_source_command_must_be_first(yadata):

    r=yadata('filter','True','!','read','d',stdin='--- {a: 1}\n')
    assert r.returncode!=0
    assert 'must be first in the pipeline' in r.stderr

def test_unsafe_yaml_rejected(yadata):

    r=yadata('filter','True',stdin='--- !!python/object/apply:os.getpid []\n')
    assert r.returncode!=0
    assert 'ConstructorError' in r.stderr

def test_plain_dicts_pass_through(yadata):

    r=yadata('filter','a>1','!','exec','b=a*10',stdin='--- {a: 1}\n--- {a: 2}\n--- {a: 3}\n')
    assert r.returncode==0,r.stderr
    assert r.stdout=='---\na: 2\nb: 20\n---\na: 3\nb: 30\n'
