
from yadata.record import Record,YadataRecord 

@YadataRecord
class Person(Record):

    yadata_tag='!Person'

    @classmethod
    def is_my_type(cls,d):
        return 'name' in d and 'surname' in d

    def __eq__(self,other):

        return self['name']==other['name'] and self['surname']==other['surname']

    def get_key_prefix(self):

        return self['surname'].lower()

    @property
    def sumbody(self):

        return sum(self['body'])

    subdir = 'Person'


