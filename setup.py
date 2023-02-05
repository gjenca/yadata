#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup,find_packages

setup (name="yadata",
       version="0.9",
       description="Managing your data the UNIX way",
       author="Gejza Jenča",
       author_email="gejza.jenca@stuba.sk",
       url="http://github.com/gjenca/yadata",
       install_requires=[
            "pyyaml","jinja2"
        ],
       packages=find_packages(),
       scripts=['scripts/yadata']
      )
