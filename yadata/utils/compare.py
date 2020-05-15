# -*- coding: utf-8 -*-

import locale

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

def cmp(val1,val2):

    if val1>val2:
        return 1
    elif val1<val2:
        return -1
    return 0

def keys_to_cmp(sort_keys):

    locale.setlocale(locale.LC_COLLATE,"")
    sgn_fieldnames=[]
    for k in sort_keys:
        if k[0]=="~":
            sgn_fieldnames.append((-1,k[1:]))
        else:
            sgn_fieldnames.append((1,k))

    def cmp_keys(d1,d2):

        for sgn,fieldname in sgn_fieldnames:
            if type(d1[fieldname]) is str:
                c=locale.strcoll(d1[fieldname],d2[fieldname])*sgn
            else:
                c=cmp(d1[fieldname],d2[fieldname])*sgn
            if c:
                return c
        return 0

    return cmp_keys

