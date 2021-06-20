# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(name='ugivia_experiments',
      version='0.9.7.1',
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
      long_description=README,
      long_description_content_type="text/markdown",
      zip_safe=False)
