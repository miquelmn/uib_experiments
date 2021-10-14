# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

LONG_DESCRIPTION = "Package to handle scientific experiments easily"

setup(name='uib_experiments',
      version='0.9.2.3',
      description='Handle the experiments.',
      long_description=LONG_DESCRIPTION,
      url='https://github.com/miquelmn/uib_experiments',
      author='Miquel Miró Nicolau, Dr. Gabriel Moyà Alcover',
      author_email='miquel.miro@uib.cat, gabriel_moya@uib.es',
      download_url = "https://github.com/miquelmn/uib_experiments/archive/refs/tags/v0.9.2.tar.gz",
      packages=find_packages(),
      install_requires=[
          'telegram_send',
          'opencv-python',
          'matplotlib',
          'scipy',
          'numpy'
      ],
      zip_safe=False)
