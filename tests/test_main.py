import io
import sys
import pytest
from yadata.main import run, c_map
from yadata.record import Record

class MainRec(Record):

    yadata_tag='!MainRec'

def yadata(monkeypatch,*args,stdin=''):

    monkeypatch.setattr(sys,'argv',['yadata',*args])
    monkeypatch.setattr(sys,'stdin',io.StringIO(stdin))
    run()

def test_help_lists_all_commands(monkeypatch,capsys):

    with pytest.raises(SystemExit) as e:
        yadata(monkeypatch,'--help')
    assert e.value.code==0
    out=capsys.readouterr().out
    for name in c_map:
        assert name in out

def test_unknown_command(monkeypatch,capsys):

    with pytest.raises(SystemExit) as e:
        yadata(monkeypatch,'frobnicate')
    assert e.value.code==2
    assert 'invalid choice' in capsys.readouterr().err

def test_mutually_exclusive_options(monkeypatch,capsys):

    with pytest.raises(SystemExit) as e:
        yadata(monkeypatch,'exec','x=1','-n','-f')
    assert e.value.code==2
    assert 'not allowed with' in capsys.readouterr().err

def test_pipeline(monkeypatch,capsys):

    yadata(monkeypatch,'filter','a!=2','!','exec','b=a*10','!','sort','-k','~a',
        stdin='--- {a: 1}\n--- {a: 2}\n--- {a: 3}\n')
    assert capsys.readouterr().out=='---\na: 3\nb: 30\n---\na: 1\nb: 10\n'

def test_bang_inside_argument_is_not_a_separator(monkeypatch,capsys):

    # only a bare '!' argument separates subcommands
    yadata(monkeypatch,'filter','a!=1','!','filter','not a',stdin='--- {a: 0}\n--- {a: 1}\n--- {a: 2}\n')
    assert capsys.readouterr().out=='---\na: 0\n'

def test_empty_input(monkeypatch,capsys):

    yadata(monkeypatch,'filter','True')
    assert capsys.readouterr().out==''

def test_render_at_end(monkeypatch,capsys,tmp_path):

    (tmp_path/'t.txt').write_text('# for r in records\n{{ r.a }}\n# endfor\n')
    yadata(monkeypatch,'filter','a>1','!','render','-t',str(tmp_path),'t.txt',
        stdin='--- !MainRec {_key: x, a: 1}\n--- !MainRec {_key: y, a: 2}\n')
    assert capsys.readouterr().out=='2\n'

def test_render_requires_records(monkeypatch,tmp_path):

    # Characterization: render works on Records only, not on plain dicts
    (tmp_path/'t.txt').write_text('')
    with pytest.raises(AttributeError):
        yadata(monkeypatch,'render','-t',str(tmp_path),'t.txt',stdin='--- {a: 1}\n')
