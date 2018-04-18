import numpy as np

from permute import MatrixPermute
from keygen import KeyGenerator

class Feistel():
    def __init__(self, lmatrix, rmatrix, subkeys):
        self.lmatrix = lmatrix
        self.rmatrix = rmatrix
        self.subkeys = subkeys
        
    def reduce_subkey(self, rmatrix, subkey):
        _subkey = []
        for i in range(8):
            seedkey = rmatrix[(i*8):((i+1)*8)].tolist()
            sbox = KeyGenerator.get_sbox(sum(seedkey))
            matkey = subkey[(i*12):((i+1)*12)]
            matkey_str = ''.join([str(x) for x in matkey])
            row, col = int(matkey_str[6], 2), int(matkey_str[6:12], 2)
            _subkey.append('{:08b}'.format(sbox[row][col]))
        return [int(c) for x in _subkey for c in x]
    
    def round_function(self, lmatrix, rmatrix, subkey):
        reduced_key = self.reduce_subkey(rmatrix, subkey)
        return xor_bit(reduced_key, lmatrix.tolist())
        
    def encipher(self):
        for i in range(16):
            temp = self.rmatrix
            self.rmatrix = self.round_function(self.lmatrix, self.rmatrix, self.subkeys[i])
            self.lmatrix = temp
    
    def decipher(self):
        inv_subkeys = self.subkeys[::-1]
        for i in range(16):
            temp = self.lmatrix
            self.lmatrix = self.round_function(self.rmatrix, self.lmatrix, inv_subkeys[i])
            self.rmatrix = temp
    
def xor_bit(bits1, bits2):
    bits1_str = ''.join([str(x) for x in bits1])
    bits2_str = ''.join([str(x) for x in bits2])
    res_xor = '{:064b}'.format(int(bits1_str, 2) ^ int(bits2_str, 2))
    return np.asarray([int(x) for x in res_xor])

if __name__=='__main__':
    import random
    
    k = KeyGenerator('hello adelle')
    matrix_permute = MatrixPermute(k.seed)
    m0 = [random.randint(0, 1) for i in range(64)]
    m0 = matrix_permute.permute(m0)
    
    m1 = [random.randint(0, 1) for i in range(64)]
    m1 = matrix_permute.permute(m1)
    f = Feistel(m0, m1, k.get_subkeys()[:16])    
    subkey = f.reduce_subkey(f.rmatrix, f.subkeys[0])
    print(subkey)
    print(xor_bit(subkey, [0] * 64))
    f.encipher()
    f.decipher()
    print(f.lmatrix.tolist()==m0.tolist())
    print(f.rmatrix.tolist()==m1.tolist())
    