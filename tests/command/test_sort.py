from yadata.command import Sort
from yadata.record import Record
from types import SimpleNamespace
import pytest

class SortRec(Record):

    yadata_tag='!SortRec'

class SortOther(Record):

    yadata_tag='!SortOther'

def sort(records,sort_key,restrict_to_type=None,restrict=None):

    ns=SimpleNamespace(sort_key=sort_key,module=[],restrict_to_type=restrict_to_type,restrict=restrict)
    return list(Sort(ns).execute(records))

def keys(records):

    return [rec['_key'] for rec in records]

def test_sort_one_key():

    records=[SortRec(_key='b',n=2),SortRec(_key='c',n=3),SortRec(_key='a',n=1)]
    assert keys(sort(records,['n']))==['a','b','c']

def test_sort_reverse():

    records=[SortRec(_key='b',n=2),SortRec(_key='c',n=3),SortRec(_key='a',n=1)]
    assert keys(sort(records,['~n']))==['c','b','a']

def test_sort_two_keys():

    records=[
        SortRec(_key='x',n=1,m=2),
        SortRec(_key='y',n=0,m=5),
        SortRec(_key='z',n=1,m=1),
    ]
    assert keys(sort(records,['n','m']))==['y','z','x']
    assert keys(sort(records,['n','~m']))==['y','x','z']

def test_sort_strings():

    # Strings are compared by locale.strcoll; avoid 'ch' and friends, whose
    # order depends on the locale (in sk_SK, 'ch' sorts after 'h')
    records=[SortRec(_key=k) for k in ['delta','alpha','echo','bravo']]
    assert keys(sort(records,['_key']))==['alpha','bravo','delta','echo']

def test_sort_restrict_to_type():

    records=[
        SortOther(_key='o2'),
        SortRec(_key='b'),
        SortOther(_key='o1'),
        SortRec(_key='a'),
    ]
    assert keys(sort(records,['_key'],restrict_to_type='SortRec'))==['a','b','o2','o1']

def test_sort_restrict():

    records=[SortRec(_key='d',n=4),SortRec(_key='c',n=3),SortRec(_key='b',n=2),SortRec(_key='a',n=1)]
    assert keys(sort(records,['_key'],restrict='n>2'))==['c','d','b','a']

def test_sort_no_key():

    with pytest.raises(ValueError):
        sort([],None)

def test_sort_missing_field():

    # Characterization: sorting on a field that some record lacks is an error
    with pytest.raises(KeyError):
        sort([SortRec(_key='a',n=1),SortRec(_key='b')],['n'])

def test_sort_restrict_with_module():

    ns=SimpleNamespace(sort_key=['_key'],module=['math'],restrict_to_type=None,restrict='math.floor(x)==1')
    records=[SortRec(_key='c',x=1.5),SortRec(_key='b',x=2.5),SortRec(_key='a',x=1.2)]
    assert keys(Sort(ns).execute(records))==['a','c','b']

def test_sort_is_stable():

    records=[SortRec(_key=k,n=0) for k in 'dbca']
    assert keys(sort(records,['n']))==list('dbca')

def test_sort_mixed_types():

    # Characterization: values that Python cannot compare raise TypeError
    with pytest.raises(TypeError):
        sort([SortRec(n=1),SortRec(n='a')],['n'])
