# -*- coding: utf-8 -*-

from ..dades import dades
from typing import Union, Tuple, List
import cv2
import os
import numpy as np
from collections.abc import Iterable
import glob
import re
import time

Num = Union[int, float]
READ_FROM_KEYBOARD = True


class Experiment:
    """ Class to handle different experiment.

    An experiment is defined by a numbe and a path. The number is the way to identify the experiment
    while the path is the location where the results will be saved.

    Args:
        path (str): Path where the different experiments will be saved.
        num_exp (int): The number of experiment. If the argument has the default value search check
                       the folder for the last experiment.
    """

    def __init__(self, path: str, num_exp: int = -1, explanation: str = None):
        if num_exp < 0:  # Is not set, we're going to get automatic the number
            exps = list(glob.iglob(os.path.join(path, "exp_*")))
            exps = sorted(exps,
                          key=lambda x: float(os.path.split(x)[-1].split(".")[0].split("_")[-1]))

            if len(exps) > 0:
                num_exp = int(os.path.split(exps[-1])[-1].split(".")[0].split("_")[-1]) + 1
            else:
                num_exp = 1

        self._num_exp = num_exp
        self._path = os.path.join(path, "exp_" + str(num_exp))
        self._start_time = 0
        self._end_time = 0
        if READ_FROM_KEYBOARD and explanation is None:
            explanation = input("Enter an explanation for the experiment: ")
        self._explanation = explanation

    def init(self) -> None:
        """ Initializes the experiment.  """

        Experiment._create_folder(self._path)
        self._start_time = time.time()

        print("Experiment %s has started." % str(self._num_exp))

    def finish(self) -> None:
        """
        Raises:
            RuntimeError when the experiment was not started
        Returns:

        """
        if self._start_time == 0:
            raise RuntimeError("ERROR: Trying to finish a non initialized experiment.")
        self._end_time = time.time()

        path = os.path.join(self._path, "experiment_resume.txt")
        with open(path, "w") as text_file:
            text_file.write(self.__get_resume())

    def __get_resume(self) -> str:
        """ Resume of the experiment.

        Constructs an string with information about the experiment.

        Returns:

        """
        elapsed_time = self._end_time - self._start_time

        print("Experiment %s finished." % str(self._num_exp))

        resum = "Experiment %s \n\tElapsed time %s" % (
            str(self._num_exp), str(elapsed_time))

        if self._explanation is not None:
            resum = resum + "\n\tExplanation: %s" % self._explanation

        return resum

    def save_result(self, data: dades.Data):
        storage_type = data.storage_type

        if dades.Data.is_image(storage_type):
            self._save_img(data)
        elif storage_type == dades.STORAGES_TYPES[2] or \
                storage_type == dades.STORAGES_TYPES[3]:
            self._save_string(data)
        elif storage_type == dades.STORAGES_TYPES[4]:
            self._save_coordinates(data)
        elif storage_type == dades.STORAGES_TYPES[1]:
            self._save_coordinates_image(data)

    def save_results_batch(self, datas: List[dades.Data]):
        """ Save data of the experiment.

        Saves a list of multiples data.

        Args:
            datas (List of data):

        Returns:

        """
        map(self.save_result, datas)

    def _save_coordinates_image(self, data: dades.Data) -> None:
        """

        Args:
            data:

        Returns:

        """

        image, coordinates = data.data

        res_image = Experiment._draw_points(image, coordinates, values=image.max() // 2, side=2)

        path, name = self._create_folders_for_data(data)

        if not re.match(".*\..{3}$", name):
            name = name + ".jpg"

        cv2.imwrite(os.path.join(path, name), res_image)

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

        path = self._create_folders_for_data(data)

        np.savetxt(path, dat, delimiter=",")

    def _save_img(self, data: dades.Data) -> None:
        """ Save the image.

        The image is saved on the path result of the combination of the global path of the class
        and the local one set in the data parameter.

        Args:
            data (dades.Data):

        Returns:

        """
        path, name = self._create_folders_for_data(data)

        if not re.match(".*\..{3}$", name):
            name = name + ".jpg"

        cv2.imwrite(os.path.join(path, name), data.data)

    def _save_string(self, data: dades.Data) -> None:
        """

        Args:
            data:

        Returns:

        """
        path, name = self._create_folders_for_data(data)

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
        if data.name is None:
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
        """
        Draw the value in the points position on the image. The drawing function used
        is a square, the side is the length of the square

        :param img:
        :param points:
        :param values:
        :param side:
        :return:
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
                int(point[0] - side): int(point[0] +
                                          side)] = val
            i = i + 1

        return mask
