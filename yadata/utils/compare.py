# -*- coding: utf-8 -*-

import locale

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

