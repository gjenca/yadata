from yadata.utils.compare import cmp_to_key

def test_cmp_to_key_ints():

    cmp_ints=lambda x,y:x-y
    key_func=cmp_to_key(cmp_ints)
    assert sorted([1,2,3],key=key_func)==[1,2,3]
    assert sorted([3,1,2],key=key_func)==[1,2,3]

