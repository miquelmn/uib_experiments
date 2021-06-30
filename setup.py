# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open('LICENSE') as f:
    LICENSE = f.read()

setup(name='ugivia_experiments',
      version='0.9.7.2',
      description='Handle the experiments.',
      url='https://gitlab.com/miquelca32/experiments',
      author='Miquel Miró Nicolau, Dr. Gabriel Moyà Alcover',
      author_email='miquel.miro@uib.cat, gabriel_moya@uib.es',
      license=LICENSE,
      package=find_packages(exclude=('texts', 'docs')),
      install_requires=[
          'telegram_send',
          'opencv-python',
          'matplotlib',
          'scipy',
          'numpy'
      ],
      zip_safe=False)
