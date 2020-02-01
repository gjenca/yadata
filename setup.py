#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup,find_packages

setup (name="yadata",
       version="alpha",
       description="Managing your data the UNIX way",
       author="Gejza Jenča",
       author_email="gejza.jenca@stuba.sk",
       url="http://bitbucket.org/gjenca/yadata",
       install_requires=[
            "pyyaml","jinja2"
        ],
       packages=find_packages(),
       scripts=['scripts/yadata']
      )
