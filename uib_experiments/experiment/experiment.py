# -*- coding: utf-8 -*-
""" Experiment module.

This module contains a set of function and classes to handles experiments. The aim of these methods
is to be able to save results easily with an standard format.
"""
from typing import Union, Tuple, List
import os
import glob
import pickle
import re
import time
import datetime
import warnings
import json

from collections.abc import Iterable

import cv2
import numpy as np
from matplotlib import pyplot as plt

from ..data import dades
from ..database_model import database

Num = Union[int, float]
DataExperiment = Union[dades.Data, List[dades.Data]]
READ_FROM_KEYBOARD = True
DONT_WRITE_TK = "REM"


class Experiment:
    """ Class to handle different experiment.

    An experiment is defined by a numbe and a path. The number is the way to identify the experiment
    while the path is the location where the results will be saved.

    Args:
        path (str): Path where the different experiments will be saved.
        num_exp (int): The number of experiment. If the argument has the default value search check
                       the folder for the last experiment.
    """

    def __init__(self, path: str, logger, num_exp: int = -1, explanation: str = None,
                 params=None, database_name: str = None):
        if num_exp < 0:  # Is not set, we're going to get automatic the number
            exps = list(glob.iglob(os.path.join(path, "exp_*")))
            exps = sorted(exps,
                          key=lambda x: float(os.path.split(x)[-1].split(".")[0].split("_")[-1]))

            if len(exps) > 0:
                num_exp = int(os.path.split(exps[-1])[-1].split(".")[0].split("_")[-1]) + 1
            else:
                num_exp = 1

        self._logger = logger
        self._num_exp = num_exp
        self.__root_path = path
        self._path = os.path.join(path, "exp_" + str(num_exp))
        self._start_time = 0
        self._end_time = 0

        if READ_FROM_KEYBOARD and explanation is None:
            explanation = input("Enter an explanation for the experiment: ")

        self.__description = explanation
        self._extra_text = None
        self.__params = params
        self.__results = None
        self.__random_state = np.random.get_state()[1][0]

        if database_name is not None:
            db = database.ExperimentDB()
            db.start(os.path.join(path, database_name))
        else:
            db = None

        self.__database_name = database_name
        self.__database = db
        self.__database_object = None

    @property
    def db_object(self):
        return self.__database_object

    @db_object.setter
    def db_object(self, value: database.Experiment):
        self.__database_object = value

    @property
    def path(self):
        return self._path

    @property
    def description(self):
        return self.__description

    @property
    def time(self):
        if self.end_time is not None:
            elapsed_time = self.end_time - self.start_time
        else:
            elapsed_time = -1

        return elapsed_time

    @property
    def results(self) -> dict:
        return self.__results

    @results.setter
    def results(self, value: dict):
        self._logger.info(f"Metrics {value}")

        if self.__database is not None:
            self.__database.add_metrics(self, value)

        self.__results = value

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def random_state(self):
        return self.__random_state

    @property
    def description(self) -> str:
        return self.__description

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self, values):
        self._logger.info(f"Params {values}")

        self.__params = values

    def get_num_exp(self) -> int:
        return self._num_exp

    def init(self):
        """ Initializes the experiment.  """

        if self.__description != DONT_WRITE_TK:
            Experiment._create_folder(self._path)
        self._start_time = time.time()

        self._logger.info(f"Experiment {self._num_exp} has started.")

    def finish(self, results=None):
        """ Finishes the experiment.

        Raises:
            RuntimeError when the experiment was not started
        """
        if self._start_time == 0:
            raise RuntimeError("ERROR: Trying to finish a non initialized experiment.")
        self._end_time = time.time()

        path = os.path.join(self._path, "experiment_resume.txt")
        if self.__description != DONT_WRITE_TK:
            with open(path, "w") as text_file:
                text_file.write(self.__get_resume())

        if self.__database is not None:
            self.__database.add_experiment(experiment=self, params=self.params, results=results)

        with open(os.path.join(self._path, "experiment.json"), "w") as outfile:
            json.dump(self.export(), outfile)

        self._logger.info(
            f"Experiment {self._num_exp} finished after {self.time}.")

    def add_metrics(self, metrics: dict):
        """ Add metrics to experiment.

        Add metrics to the experiment. In the case that there is a database object also update it
        to contain this information.

        Args:
            metrics (dict): Dictionary containing the metrics in a {metric_name => metric_value}
        """
        self._logger.info(f"Metrics {metrics}")

        if self.__database is not None:
            self.__database.add_metrics(self, metrics)

    def set_explanation(self, explanation: str):
        """ Warning: Deprecated

        Sets the description of the algorithm

        Args:
            explanation (str):

        """
        warnings.warn("Endpoint deprecated, use instead set_description")
        self.set_description(explanation)

    def set_description(self, description: str):
        """ Sets the description of the algorithm

        Args:
            description (str):

        """
        self.__description = description

    def __get_resume(self) -> str:
        """ Resume of the experiment.

        Constructs an string with information about the experiment.

        """
        resum = "%s \tExperiment %s started" % (
            datetime.datetime.fromtimestamp(self._start_time).strftime("%d/%m/%Y %H:%M:%S"),
            str(self._num_exp))

        if self.__description is not None:
            resum += "\n\t\t\t%s" % self.__description

        if self.__params is not None:
            resum += "\n\t\t\targs: " + str(self.__params)

        if self._extra_text is not None:
            resum = resum + "\n\t\t\t %s" % self._extra_text

        resum += f"\n\t\t\tElapsed time {self.time} minutes"
        resum += "\n%s \tExperiment %s finished" % (
            datetime.datetime.fromtimestamp(self._end_time).strftime("%d/%m/%Y %H:%M:%S"),
            str(self._num_exp))

        return resum

    def save_result(self, dada: DataExperiment):
        """
        
        Args:
            dada:

        """
        if self.__description != DONT_WRITE_TK:
            if isinstance(dada, List):
                self.__save_results_batch(dada)
            else:
                self.__save_result_single(dada)

    def __save_result_single(self, dada: dades.Data):
        """
        
        Args:
            dada:

        """
        storage_type = dada.storage_type

        if dades.Data.is_image(storage_type):
            self._save_data_img(dada)
        elif storage_type == dades.STORAGES_TYPES[2]:
            self._save_string(dada)
        elif storage_type == dades.STORAGES_TYPES[3]:
            self.__save_object(dada)
        elif storage_type in (dades.STORAGES_TYPES[4], dades.STORAGES_TYPES[7]):
            self._save_coordinates(dada)
        elif storage_type == dades.STORAGES_TYPES[1]:
            self._save_coordinates_image(dada)
        elif storage_type == dades.STORAGES_TYPES[10]:
            self._save_coordinates_values_images(dada)

    def __save_object(self, data: dades.Data):
        """ Pickle object

        """
        path, name = self._create_folders_for_data(data)

        with open(path + "/" + name + '.pickle', 'wb') as handle:
            pickle.dump(data.data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return None

    def __save_results_batch(self, datas: List[dades.Data]):
        """ Save data of the experiment.

        Saves a list of multiples data.

        Args:
            datas (List of data):

        Returns:

        """
        [self.save_result(dat) for dat in datas]

    def _save_coordinates_values_images(self, datas: dades.Data) -> None:
        """ Save image with value for coordinates.

        Expects three types of data. The first of all the image. An image is a numpy matrix. The
        second one the coordinates. Should be a array with two columns one for every dimension.
        The third one a value for every one of the coordinates.

        Save an image with the values drawed over the original image in the points indicated by the
        coordinates.

        Args:
            datas:

        Returns:
            None

        Raises:
            Value error if the values and the coordinates are not of the same length.
        """
        image, coordinates, values = datas.data
        image = np.copy(image)

        if len(coordinates) != len(values):
            raise ValueError("Coordinates and values should have the same length.")

        image[image > values.max()] = values.max() + 5

        curv_img = Experiment._draw_points(image, coordinates, values, 0).astype(np.uint8) * 255
        curv_img = Experiment.__apply_custom_colormap(curv_img)

        self.__save_img(datas, curv_img)

    def add_text(self, text: str) -> None:
        """
        Add a text into the resume file.


        Args:
            text: String with the text to add

        """

        if self._extra_text is None:
            self._extra_text = text
        else:
            self._extra_text = self._extra_text + "\n" + text

    def _save_coordinates_image(self, data: dades.Data) -> None:
        """

        Args:
            data:

        Returns:

        """

        image, coordinates = data.data

        res_image = Experiment._draw_points(image, coordinates, values=image.max() // 2, side=2)

        self.__save_img(data, res_image)

    def _save_coordinates(self, data: dades.Data) -> None:
        """

        Args:
            data:

        Returns:

        Raises:


        """
        dat = data.data
        if not isinstance(dat, np.ndarray):
            raise ValueError("Not a valid data for the coordinates.")

        path, name = self._create_folders_for_data(data)

        np.savetxt(os.path.join(path, name + ".csv"), dat, delimiter=",")

    def _save_data_img(self, data: dades.Data) -> None:
        """ Save the image.

        The image is saved on the path result of the combination of the global path of the class
        and the local one set in the data parameter.

        Args:
            data (dades.Data):

        Returns:

        """
        self.__save_img(data, data.data)

    def __save_img(self, data: dades.Data, image: np.ndarray):
        path, name = self._create_folders_for_data(data)

        if not re.match(".*\..{3}$", name):
            name = name + ".png"

        cv2.imwrite(os.path.join(path, name), image)

    def _save_string(self, data: dades.Data) -> None:
        """

        Args:
            data:

        Returns:

        """
        path, _ = self._create_folders_for_data(data)

        with open(path, "w") as text_file:
            text_file.write(data.data)

    def _create_folders_for_data(self, data: dades.Data) -> Tuple[str, str]:
        """ Create recursively the folder tree.

        Args:
            data:

        Returns:

        """
        path = os.path.join(self._path, data.path)

        Experiment._create_folder(path)

        name = data.name
        if name is None:
            files = list(glob.iglob(os.path.join(path, "*")))
            name = str(len(files))

        return path, name

    @staticmethod
    def _create_folder(path):
        """ Create recursively the folder tree.

        Args:
            path:

        Returns:

        """

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    @staticmethod
    def _draw_points(img, points, values, side=0):
        """ Draw the value in the points position on the image. The drawing function used
        is a square, the side is the length of the square

        Args:
            img:
            points:
            values:
            side:

        Returns:

        """
        mask = np.copy(img)
        mask = mask.astype(np.float32)

        i = 0
        for point in points:
            if isinstance(values, Iterable):
                val = values[i]
            else:
                val = values
            if side == 0:
                mask[point[1], point[0]] = val
            else:
                mask[int(point[1] - side): int(point[1] + side),
                int(point[0] - side): int(point[0] + side)] = val
            i = i + 1

        return mask

    @staticmethod
    def __apply_custom_colormap(image_gray, cmap=plt.get_cmap('viridis')):
        """ Applies a CMAP from matplotlib to a gray-scale image.

        Args:
            image_gray:
            cmap:

        Returns:

        """
        assert image_gray.dtype == np.uint8, 'must be np.uint8 image'
        if image_gray.ndim == 3: image_gray = image_gray.squeeze(-1)

        # Initialize the matplotlib color map
        sm = plt.cm.ScalarMappable(cmap=cmap)

        # Obtain linear color range
        color_range = sm.to_rgba(np.linspace(0, 1, 256))[:, 0:3]  # color range RGBA => RGB
        color_range = (color_range * 255.0).astype(np.uint8)  # [0,1] => [0,255]
        color_range = np.squeeze(
            np.dstack([color_range[:, 2], color_range[:, 1], color_range[:, 0]]),
            0)  # RGB => BGR

        # Apply colormap for each channel individually
        channels = [cv2.LUT(image_gray, color_range[:, i]) for i in range(3)]
        return np.dstack(channels)

    def export(self) -> dict:
        """ Exports experiment to a dict.

        Returns:
            Experiment info
        """
        info = {'path': self.__root_path, 'description': self.__description,
                'num_exp': self._num_exp, 'random_state': int(self.__random_state),
                'end_time': self._end_time, 'start_time': self._start_time, 'params': self.params,
                'database_name': self.__database_name}

        if self.__params is not None:
            info['params'] = self.__params

        if self.__database is not None:
            info['id_database'] = self.__database_object.exp_id

        return info

    @staticmethod
    def import_from_json(path: str, logger):
        """ Import Experiment info from json file.

        Imports the Experiment information previously exported with the respective function.

        Args:
            path (str): Path to the file containing the info.
            logger (logger): Python logger object

        Returns:
            Experiment object with the information found in the file (path).
        """
        exp = None

        with open(path, "r") as infile:
            data = json.load(infile)
            exp = Experiment(path=data['path'], num_exp=data['num_exp'], params=data['params'],
                             explanation=data['description'], database_name=data['database_name'],
                             logger=logger)

            if 'id_database' in data:
                db_exp = database.Experiment.get(exp_id=data['id_database'])
                exp.db_object = db_exp

        return exp
