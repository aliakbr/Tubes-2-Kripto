import hashlib
import random
import numpy as np

from functools import reduce

class MatrixPermute():
    def __init__(self, seed):
        self.seed = seed

    def generate_numbers(self):
        random.seed(self.seed)
        return [random.randint(0, 7) for i in range(4)]

    def permute(self, bits, reverse=False):
        '''
        For decryption, set reverse=True
        '''
        if len(bits) != 64:
            raise Exception('Length of bits must be 64')
        matrix = np.array(bits).reshape((8, 8))
        nums = self.generate_numbers()

        for i in range(4):
            self.spin(matrix, i, nums[i], (i % 2 == 0) != reverse)
        return matrix.reshape((64,))

    def spin(self, matrix, level, n, clockwise):
        nums = []
        end_idx = len(matrix) - level
        for j in range(level, end_idx):
            nums.append(matrix[level, j])
        for i in range(level+1, end_idx-1):
            nums.append(matrix[i, end_idx-1])

        for j in range(end_idx-1, level-1, -1):
            nums.append(matrix[end_idx-1, j])
        for i in range(end_idx-2, level, -1):
            nums.append(matrix[i, level])

        nums = self.circular_shift(nums, n % len(nums), clockwise)
        c = 0
        for j in range(level, end_idx):
            matrix[level, j] = nums[c]
            c += 1
        for i in range(level+1, end_idx-1):
            matrix[i, end_idx-1] = nums[c]
            c += 1

        for j in range(end_idx-1, level-1, -1):
            matrix[end_idx-1, j] = nums[c]
            c += 1
        for i in range(end_idx-2, level, -1):
            matrix[i, level] = nums[c]
            c += 1

    def circular_shift(self, bits, n, clockwise):
        if clockwise:
            return bits[n:] + bits[:n]
        return bits[-n:] + bits[:-n]
