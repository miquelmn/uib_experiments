# -*- coding: utf-8 -*-

import json
from typing import List, Tuple


class Data:
    """

    """

    def __init__(self, data, storage_type: str, path: str):
        """

        Args:
            data:
            storage_type:
            path:
        """
        self._data = data

        if not (storage_type == "I" or storage_type == "S" or storage_type == "O" or
                storage_type == "C" or storage_type == "CI"):
            raise ValueError("Not a valid data type")

        self._storage_type = storage_type
        self._path = path

    @property
    def data(self):
        """

        Returns:

        """
        if self._storage_type == "O":
            data = json.dumps(self._data.__dict__)
        else:
            data = self._data

        return data

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

#
# class MultipleData():
#
#     def __init__(self, data: List[Tuple[object, str]], path: str):
#         self.__data = []
#         for i, (info, type) in enumerate(data):
#             path =

