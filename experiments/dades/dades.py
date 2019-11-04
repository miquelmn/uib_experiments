# -*- coding: utf-8 -*-
"""Auxiliar function for concave points calculation.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.


.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import numpy as np

STORAGES_TYPES = ["color_image", "coordinates_image", "string", "object", "coordinates",
                  "coordinates_values", "squares", "ellipses", "binary_image", "column",
                  "coordinates_values_image"]


class Data:
    """


    """

    def __init__(self, data, path: str, name: str = None):
        """

        Args:
            data :
            path (str):
            name (str)
        Raises:
            ValueError if the storage type is not known.
        """

        self._data = data

        # if storage_type not in ALLOW_STORAGES_TYPES:
        # raise ValueError("Not a valid data type")

        self._storage_type = self._discover_type()
        self._path = path
        self._name = name

    def _discover_type(self) -> str:
        """ Discover the type of the data.

        Discovers the data type. The values can only be the ones saved on the _STORAGE_TYPES array.

        Returns:
            String with the type of the values.
        """
        storage_type = None
        if isinstance(self.data, str):
            storage_type = STORAGES_TYPES[2]
        elif isinstance(self.data, np.ndarray):
            storage_type = self._discover_numpy(self.data)
        elif isinstance(self.data, tuple):
            if len(self.data) == 2:
                first, second = self.data
                first_type = self._discover_numpy(first)
                second_type = self._discover_numpy(second)
                if self.is_image(first_type) and second_type == STORAGES_TYPES[4]:
                    storage_type = STORAGES_TYPES[1]
            elif len(self.data) == 3:
                first, second, third = self.data
                first_type = self._discover_numpy(first)
                second_type = self._discover_numpy(second)
                third_type = self._discover_numpy(third)

                if self.is_image(first_type) and second_type == STORAGES_TYPES[4] \
                        and third_type == STORAGES_TYPES[9]:
                    storage_type = STORAGES_TYPES[10]
        elif isinstance(self.data, object):
            storage_type = STORAGES_TYPES[3]

        if storage_type is None:
            raise ValueError("Unknown data type.")

        return storage_type

    @staticmethod
    def is_image(tipus: str) -> bool:
        return tipus in (STORAGES_TYPES[0], STORAGES_TYPES[8])

    @staticmethod
    def _discover_numpy(data: np.ndarray) -> str:
        """ Discovers witch type of numpy data is.

        Depending on the shape and the length of the axis is possible to get the type. There are six
        numpy types:

        Types:
            color_image: Numpy array with three channels. Represents an image with color.
            binary_image: Numpy array with two channels and with more than 5 columns.
            coordinates: Numpy array with two channels and with two columns.
            coordinates_values


        Args:
            data (ndarray): Numpy array to discover the type.

        Returns:

        """
        storage_type = None

        if len(data.shape) == 2:
            if data.shape[1] == 2:
                storage_type = STORAGES_TYPES[4]
            elif data.shape[1] == 3:
                storage_type = STORAGES_TYPES[5]
            elif data.shape[1] == 4:
                storage_type = STORAGES_TYPES[6]
            elif data.shape[1] == 5:
                storage_type = STORAGES_TYPES[7]
            else:
                storage_type = STORAGES_TYPES[8]
        elif len(data.shape) == 3:
            storage_type = STORAGES_TYPES[0]
        elif len(data.shape) == 1:
            storage_type = STORAGES_TYPES[9]

        if storage_type is None:
            raise ValueError("Unknown numpy format.")

        return storage_type

    @property
    def data(self):
        """

        Returns:

        """

        return self._data

    @property
    def storage_type(self):
        """

        Returns:

        """
        return self._storage_type

    @property
    def path(self):
        """

        Returns:

        """
        return self._path

    @property
    def name(self):
        """

        Returns:

        """

        return self._name
