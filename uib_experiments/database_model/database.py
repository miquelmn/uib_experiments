# -*- coding: utf-8 -*-
""" Database module.

This module wrapper an ORM (peewee) to connect the experiments with a relational database.

Written by: Miquel Miró Nicolau (UIB)
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
            path: String with the path to the database.

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
            experiment: Experiment to add to the database.
            params: (optional) Dictionary with the parameters information.
            results: (optional) Dictionary with the results information.

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
    def add_metrics(experiment: exp, results: Dict, theta: int = None):
        """ Add the metrics to the database.

        This method adds the metrics to the database. A metric is a tuple with the name and the
        value. In addition can also have a theta value. This value is the distance used to compute
        the different metrics.

        Args:
            experiment: Experiment of whom the metrics are.
            results: Metrics to add to the database.
            theta: Integer with the theta value.

        """
        ExperimentDB.__add_elements(results, experiment.db_object.results, Result, theta)

    @staticmethod
    def __add_elements(data, table, class_object, theta: int = None):
        """ Add elements to the database.

        Args:
            data: Dictionary with the data to add to the database
            table: Table from the peerwee database.
            class_object: Class of the object to add to the database.
            theta: (optional) Integer with the theta value. The distance to be used to calculate the
                    metrics.
        """
        for name, value in data.items():
            if theta is None:
                element = class_object.get_or_none(name=name, value=value)
            else:
                element = class_object.get_or_none(name=name, value=value, theta=theta)

            if element is None and theta is None:
                class_object.create(name=name, value=value)
            elif element is None and theta is not None:
                class_object.create(name=name, value=value, theta=theta)

            if theta is None:
                query = table.select().where(class_object.name == name,
                                             class_object.value == value)
            else:
                query = table.select().where(class_object.name == name, class_object.theta == theta,
                                             class_object.value == value)

            if not query.exists():
                table.add(element)

    @staticmethod
    def add_params(experiment: exp, params: Dict):
        """ Add parameters to the database.

        Parameters are a tuple with the name and the value of the parameter. We add to the database
        with this same format.

        Args:
            experiment: Experiment of whom the parameters are.
            params: Dictionary with the parameters to add to the database.

        """
        ExperimentDB.__add_elements(params, experiment.db_object.params, Param)

    @staticmethod
    def get_experiment(identifier: int):
        return Experiment.get(Experiment.exp_id == identifier)


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
    theta = IntegerField(null=True)
    experiments = ManyToManyField(Experiment, backref='results')


class Param(BaseModel):
    """ Param model

    A parameter is a defined as a tuple (key, value) containing the information of the parameters of
    the experiment.
    """
    name = CharField()
    value = CharField()
    experiments = ManyToManyField(Experiment, backref='params')
