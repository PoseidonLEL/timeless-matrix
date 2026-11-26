from operator import index as integer_index

import numpy as np


class timeless_matrix:

    def __init__(self, array):
        self.array = np.array(array, dtype=np.float32, copy=True)
        if (self.array.ndim != 2):
            raise ValueError("Expected a 2D matrix.")
        self.array_history = [self.array.copy()]

    #Insert one row (axis=0) or column (axis=1).
    def add_to_array(self, value, index=None, to_end=False, axis=0):
        axis = integer_index(axis)
        if (axis not in (0, 1)):
            raise ValueError("Use axis=0 for rows or axis=1 for columns.")
        size = self.array.shape[axis]
        position = size if to_end else integer_index(index)
        if (position < -size or position > size):
            raise IndexError("Insertion index out of range.")

        line = np.asarray(value, dtype=np.float32)
        if (line.shape != (self.array.shape[1-axis],)):
            raise ValueError("Provide one row or column of matching length.")
        updated = np.insert(self.array, position, line, axis=axis)
        self.update_history(updated)
        self.array = updated

    #Remove one row (axis=0) or column (axis=1).
    def remove_from_array(self, index, axis=0):
        axis = integer_index(axis)
        if (axis not in (0, 1)):
            raise ValueError("Use axis=0 for rows or axis=1 for columns.")
        updated = np.delete(self.array, integer_index(index), axis=axis)
        self.update_history(updated)
        self.array = updated

    #Restore selected (row, column) pairs or the entire historical matrix.
    def rewind(self, index=None, how_far_back=None, revert_entire_array=False): 
        steps = integer_index(how_far_back)
        if (steps < 0 or steps >= len(self.array_history)):
            raise IndexError("Requested history is out of range.")
        past = self.array_history[-1-steps]

        if (revert_entire_array):
            updated = past.copy()
            self.update_history(updated)
            self.array = updated
            return

        pairs = np.asarray(index)
        if (pairs.shape == (0,)):
            pairs = np.empty((0, 2), dtype=np.intp)
        if (pairs.shape == (2,)):
            pairs = pairs.reshape(1, 2)
        if (pairs.ndim != 2 or pairs.shape[1] != 2 or pairs.dtype.kind not in 'iu'):
            raise TypeError("Expected integer (row, column) pairs.")

        for axis, coordinates in enumerate(pairs.T):
            if (coordinates.size):
                low, high = int(coordinates.min()), int(coordinates.max())
                if (low < -past.shape[axis] or high >= past.shape[axis]):
                    raise IndexError("Index does not exist in this past instance!")
        rows, columns = pairs.astype(np.intp, copy=False).T
        self.array[rows, columns] = past[rows, columns]
        self.update_history(self.array)

    def update_history(self, new_array):
        snapshot = np.array(new_array, dtype=np.float32, copy=True)
        if (snapshot.ndim != 2):
            raise ValueError("Expected a 2D matrix.")
        self.array_history.append(snapshot)
