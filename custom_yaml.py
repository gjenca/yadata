#!/usr/bin/env python3
import sys
from ruamel.yaml import YAML, yaml_object

yaml = YAML()


@yaml_object(yaml)
class User(dict):
    yaml_tag = u'!user'

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_mapping(cls.yaml_tag, node)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(constructor.construct_mapping(node))


yaml.dump([User(a=1,b=[1,2,3])], sys.stdout)
