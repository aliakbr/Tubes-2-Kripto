from feistel import Feistel
from keygen import KeyGenerator
from permute import MatrixPermute

class PEA():
    def __init__(self, key):
        self.key_gen = KeyGenerator(key)
        self.matrix_permute = MatrixPermute(self.key_gen.seed)
        self.subkeys = self.key_gen.get_subkeys()

    def encrypt(self, bits, decrypt=False):
        '''
            bits: list of 0s and 1s
        '''
        if len(bits) != 256:
            raise Exception('Length of bits must be 256')
        b1, b2, b3, b4 = bits[:64], bits[64:128], bits[128:192], bits[192:256]
        m1 = self.matrix_permute.permute(b1)
        m2 = self.matrix_permute.permute(b2)
        m3 = self.matrix_permute.permute(b3)
        m4 = self.matrix_permute.permute(b4)

        subkeys_1 = self.subkeys[:16]
        f1 = Feistel(m1, m2, subkeys_1)
        if decrypt:
            f1.decipher()
        else:
            f1.encipher()

        subkeys_2 = self.subkeys[16:32]
        f2 = Feistel(m3, m4, subkeys_2)
        if decrypt:
            f2.decipher()
        else:
            f2.encipher()

        m1 = self.matrix_permute.permute(f1.lmatrix, True)
        m2 = self.matrix_permute.permute(f1.rmatrix, True)
        m3 = self.matrix_permute.permute(f2.lmatrix, True)
        m4 = self.matrix_permute.permute(f2.rmatrix, True)

        return m1.tolist() + m2.tolist() + m3.tolist() + m4.tolist()
