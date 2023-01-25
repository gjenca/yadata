# -*- coding: utf-8 -*-

import locale
from functools import total_ordering,cache

@cache
def make_key(key_tuple):

  return cmp_to_key(keys_to_cmp(key_tuple))

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    @total_ordering
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
    return K

def cmp(val1,val2):

    if val1>val2:
        return 1
    elif val1<val2:
        return -1
    return 0

@cache
def deep_getitem(fieldref):

    def ret_f(rec):
    
        to_ret=rec
        for fieldname in fieldref.split('.'):
            to_ret=to_ret[fieldname]
        return to_ret

    return ret_f

@cache
def keys_to_cmp(sort_keys):

    locale.setlocale(locale.LC_COLLATE,"")
    sgn_field_refs=[]
    for k in sort_keys:
        if k[0]=="~":
            sgn_field_refs.append((-1,k[1:]))
        else:
            sgn_field_refs.append((1,k))

    def cmp_keys(d1,d2):

        for sgn,field_ref in sgn_field_refs:
            value1=(deep_getitem(field_ref))(d1)
            value2=(deep_getitem(field_ref))(d2)
            if type(value1) is str and type(value2) is str:
                c=locale.strcoll(value1,value2)*sgn
            else:
                c=cmp(value1,value2)*sgn
            if c:
                return c
        return 0

    return cmp_keys

