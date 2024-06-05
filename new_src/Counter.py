import numpy as np
from typing import Callable

class Counter:
    def __init__(self, dtype = int, start_array_size = 16):
        self.entry_lookup = {}
        self.dtype = dtype
        self.num_elems = 0
        self.array_size = start_array_size
        self.array = np.zeros((self.array_size,), dtype=self.dtype)
    
    def add(self, key: str, start) -> None:
        if self.num_elems == self.array_size:
            self.array = np.concatenate((self.array, np.zeros((self.array_size,), dtype=self.dtype)))
        self.entry_lookup[key] = self.num_elems
        self.array[self.num_elems] = start
        self.num_elems += 1
    
    def add_all(self, val) -> None:
        if self.num_elems > 0:
            self.array[0:self.num_elems] += val

    def subtract_all(self, val) -> None:
        if self.num_elems > 0:
            self.array[0:self.num_elems] -= val

    def apply_all(self, func: Callable) -> None:
        if self.num_elems > 0:
            self.array[0:self.num_elems] = func(self.array[0:self.num_elems])

    def get(self, key: str):
        return self.array[self.entry_lookup[key]]