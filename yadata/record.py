
import shutil
import os
import errno
import tempfile
import yadata.utils.sane_yaml as sane_yaml
import yaml
from collections import namedtuple
import sys
sys.path.insert(0,'')

ManyToMany=namedtuple('ManyToMany',['fieldname','inverse_type','inverse_fieldname','sort_by','inverse_sort_by'])
OneToMany=namedtuple('OneToMany',['fieldname','inverse_type','inverse_fieldname','inverse_sort_by'])

def AddManyToMany(fieldname,inverse_type,inverse_fieldname,sort_by=None,inverse_sort_by=None):

    def decorate(cls):
    
        cls._many_to_many.append(ManyToMany(fieldname,inverse_type,inverse_fieldname,sort_by,inverse_sort_by))
        inverse_type._inverse.append(inverse_fieldname)
        return cls
    return decorate

def AddOneToMany(fieldname,inverse_type,inverse_fieldname,inverse_sort_by=None):

    def decorate(cls):
        
        cls._one_to_many.append(OneToMany(fieldname,inverse_type,inverse_fieldname,inverse_sort_by))
        inverse_type._inverse.append(inverse_fieldname)
        return cls
   
    return decorate

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise

class LogEntry:
    
    def __init__(self,_key,method,fieldname,oldvalue,newvalue):

        self._key=_key
        self.method=method
        self.fieldname=fieldname
        self.oldvalue=oldvalue
        self.newvalue=newvalue

    def __repr__(self):

        return f"_key={self._key}[{self.fieldname}] {self.oldvalue}->{self.newvalue} (method:{self.method})"

class MetaRecord(type):
    
    def __new__(cls,*args,**kwargs):
        
        instance_class=super(MetaRecord,cls).__new__(cls,*args,**kwargs)
        instance_class._many_to_many=[]
        instance_class._one_to_many=[]
        instance_class._inverse=[]

        if 'yadata_tag' in dir(instance_class):

            def cls_representer(dumper,data):

                d=dict(data)
                for inverse_field in instance_class._inverse:
                    if inverse_field in d:
                        del d[inverse_field]
                return dumper.represent_mapping(instance_class.yadata_tag,d,flow_style=None)

            def cls_constructor(loader,node):

                dict_value=loader.construct_mapping(node)
                return instance_class(dict_value)

            yaml.add_representer(instance_class,cls_representer)
            yaml.add_constructor(instance_class.yadata_tag,cls_constructor)

        return instance_class

class Record(dict,metaclass=MetaRecord):
    """ Base class for all types of records.
"""

#    _many_to_many=[]
#    _one_to_many=[]

    top_fields=[]


    def __init__(self,*args,**kwargs):
        d=dict(*args,**kwargs)
        if not self.is_my_type(d):
           raise TypeError(f"Yadata type of {d} is not {type(self).yadata_tag}")
        dict.__init__(self,d)
        self.path=None
        self.dirty=False

    def __new__(cls,*args,**kwargs):

        instance=super(Record,cls).__new__(cls,*args,**kwargs)
        for fieldname in cls._inverse:
            instance[fieldname]=[]
        return instance

    def __setitem__(self,key,value):
        self.dirty=True
        dict.__setitem__(self,key,value)

    def __repr__(self):
        
        typename=type(self).__name__
        dictrepr=dict.__repr__(self)

        return f'{typename}({dictrepr})'

    def generate_keys(self):

        prefix=self.get_key_prefix()
        yield prefix
        i=0
        while True:
           yield f"{prefix}_{i}"
           i+=1

    def save(self,datadir):

        if not self.dirty:
            return
        
        if not "_key" in self:
            for key in self.generate_keys():
                if key not in datadir.keys:
                    self["_key"]=key
                    break
        
        if self.path is None:
            pathdir=os.path.join(datadir.dirname,self.subdir)
            mkdir_p(pathdir)
            self.path=os.path.join(pathdir,("%s.yaml" % self["_key"]))
        f=tempfile.NamedTemporaryFile(delete=False,mode='w')
        f.write(sane_yaml.dump(self))
        f.close()
        shutil.move(f.name,self.path)

    
    def method_SET(self,field,value):

        self[field]=value

    def method_UNION(self,field,value):

        self[field]=list(set(self[field]+value))

    def method_EXTEND(self,field,value):

        self[field].extend(value)

    def method_DELETE(self,field,value=None):

        del self[field]
        self.dirty=True
   
    method_dispatcher={
        "set":method_SET,
        "union":method_UNION,
        "extend":method_EXTEND,
        "delete":method_DELETE,
    }


    def merge(self,other,methods):
       
        if "_key" not in self:
            raise ValueError("Attempted to merge with a record without key")
        bounced={}
        log=[]
        for field in other:
            if field not in self:
                self[field]=other[field]
                log.append(LogEntry(self["_key"],"new-field",field,None,other[field]))
            elif self[field]!=other[field]:
                if field not in methods:
                    bounced[field]=other[field]
                else:
                    old_value=self[field]
                    self.method_dispatcher[methods[field]](self,field,other[field])
                    log.append(LogEntry(self["_key"],methods[field],field,old_value,self[field]))
        if bounced:
            bounced["_key"]=self["_key"]
            return bounced,log
        else:
            return {},log
