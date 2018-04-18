import hashlib
import random
import numpy as np

from functools import reduce

class KeyGenerator():
    def __init__(self, keyInput):
        self.md5_key = hashlib.md5(str(keyInput).encode('ascii')).digest()
        self.seed = self.seed_int(self.md5_key[0:4])
        self.key = self.md5_key[4:]

    def get_subkeys(self):
        subkeys = []
        fibonacci = [1, 1]
        key_bits = self.bit_from_bytes(self.key)
        random.seed(self.seed)
        random.shuffle(key_bits)

        left = key_bits[:48]
        right = key_bits[48:]
        for i in range(32):
            subkey = left + right
            random.shuffle(subkey)
            subkeys.append(subkey)
            left = self.circular_shift(left, fibonacci[-1])
            right = self.circular_shift(right, fibonacci[-1])
            fibonacci.append(fibonacci[-1] + fibonacci[-2])
        return subkeys

    def circular_shift(self, bits, n):
        n = n % 48
        return bits[n:] + bits[:n]

    def bit_from_bytes(self, bytes):
        bits = ''
        for byte in bytes:
            bits += format(byte, 'b').zfill(8)
        return list(map(lambda x: int(x), bits))

    def seed_int(self, seed):
        return reduce((lambda x, y: x * y), seed)
    
    @classmethod
    def get_sbox(cls, seed):
        init_list = [x for x in range(256)] * 16
        random.seed(seed)
        random.shuffle(init_list)
        sbox_arr = np.asarray(init_list)
        return np.reshape(sbox_arr, (64, 64))

if __name__ == '__main__':
    key_gen = KeyGenerator('hello adele')
    print(key_gen.get_subkeys())
    print(len(key_gen.get_subkeys()))
    print(len(key_gen.get_subkeys()[0]))
    sbox_arr = KeyGenerator.get_sbox(16)
    print(sbox_arr)
