# -*- coding: utf-8 -*-
""" Database module.

This module wrapper an ORM (peewee) to connect the experiments with a relational database.
"""
from typing import Dict
import datetime
import os

from peewee import *

from uib_experiments.experiment import experiment as exp

DB = SqliteDatabase(None)


class ExperimentDB:

    @staticmethod
    def start(path: str):
        """
        Initialize the database in the case that do not exist, otherwise it connects the method the
        library to the peewee handler

        Args:
            path:

        """
        is_created = os.path.isfile(path)

        DB.init(path)

        DB.connect()
        if not is_created:
            results_experiments = Result.experiments.get_through_model()
            params_experiments = Param.experiments.get_through_model()

            DB.create_tables([Experiment, Result, Param, results_experiments, params_experiments])

    @staticmethod
    def add_experiment(experiment: exp, params: Dict = None, results: Dict = None):
        """ Add an experiment to the DataBase.

        This method adds an experiment to the database. In addition of the solo experiment can also
        add to the database the parameters information and the results information.

        Args:
            experiment (Experiment):
            params (Dict):
            results (Dict):

        """
        inst_exp = Experiment.create(start_date=experiment.start_time, end_date=experiment.end_time,
                                     random_state=experiment.random_state,
                                     folder_path=experiment.path,
                                     description=experiment.description)

        experiment.db_object = inst_exp

        if params is None:
            params = {}

        if results is None:
            results = {}

        ExperimentDB.add_params(experiment, params)
        ExperimentDB.add_metrics(experiment, results)

    @staticmethod
    def add_metrics(experiment: exp, results: Dict):
        for name, value in results.items():
            res = Result.get_or_none(name=name, value=value)

            if res is None:
                res = Result.create(name=name, value=value)

            query = experiment.db_object.results.select().where(Result.name == name,
                                                                Result.value == value)

            if not query.exists():
                experiment.db_object.results.add(res)

    @staticmethod
    def add_params(experiment: exp, params: Dict):
        for name, value in params.items():
            param = Param.get_or_none(name=name, value=value)

            if param is None:
                param = Param.create(name=name, value=value)

            query = experiment.db_object.params.select().where(Param.name == name,
                                                               Param.value == value)

            if not query.exists():
                experiment.db_object.params.add(param)

    @staticmethod
    def get_experiment(id: int):
        return Experiment.get(Experiment.exp_id == id)


class BaseModel(Model):
    class Meta:
        database = DB


class Experiment(BaseModel):
    """ Experiment model.

    Model for the sql database. It contains a set of field that are saved to the database.
    """
    exp_id = AutoField(unique=True, primary_key=True)

    start_date = DateTimeField(default=datetime.datetime.now)
    end_date = DateTimeField(default=datetime.datetime.now)
    random_state = IntegerField()
    folder_path = CharField()
    description = CharField()


class Result(BaseModel):
    """ Results model

    A result is a defined as a tuple (key, value) containing the information of the parameters of
    the experiment.
    """
    name = CharField()
    value = CharField()
    experiments = ManyToManyField(Experiment, backref='results')


class Param(BaseModel):
    """ Param model

    A parameter is a defined as a tuple (key, value) containing the information of the parameters of
    the experiment.
    """
    name = CharField()
    value = CharField()
    experiments = ManyToManyField(Experiment, backref='params')
