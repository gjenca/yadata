from yadata.utils.compare import keys_to_cmp

da1b2={'a':1,'b':2}
da2b1={'a':2,'b':1}
da1b1={'a':1,'b':1}


def test_keys_to_cmp_one_key_a():

    cmp_this=keys_to_cmp(['a'])
    assert cmp_this(da1b2,da2b1)<0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da2b1,da1b1)>0

def test_keys_to_cmp_two_keys_a_b():

    cmp_this=keys_to_cmp(['a','b'])
    assert cmp_this(da1b2,da1b1)>0
    assert cmp_this(da1b1,da1b2)<0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da1b2,da2b1)<0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da2b1,da1b1)>0

def test_keys_to_cmp_two_keys_a_neg_b():

    cmp_this=keys_to_cmp(['a','~b'])
    assert cmp_this(da1b2,da1b1)<0
    assert cmp_this(da1b1,da1b2)>0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da1b2,da2b1)<0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da2b1,da1b1)>0

def test_keys_to_cmp_two_keys_neg_a_neg_b():
    cmp_this=keys_to_cmp(['~a','~b'])
    assert cmp_this(da1b2,da1b1)<0
    assert cmp_this(da1b1,da1b2)>0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da1b2,da2b1)>0
    assert cmp_this(da1b1,da1b1)==0
    assert cmp_this(da2b1,da1b1)<0
