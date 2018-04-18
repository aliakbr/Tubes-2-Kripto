from pea import PEA
from collections import Counter
import numpy as np
import time

def ECB(text, key, decrypt=False):
    fullbits = text_to_bits(text)

    pea = PEA(key)
    bits_encrypt = []
    for i in range(int(len(fullbits)/256)):
        bits = fullbits[(i*256):((i+1)*256)]
        bits_encrypt.extend(pea.encrypt(bits, decrypt))

    return bits_to_text(bits_encrypt)

def CBC(text, key, init_vector, decrypt=False):
    fullbits = text_to_bits(text)

    pea = PEA(key)
    last_bits = init_vector
    bits_encrypt = []
    for i in range(int(len(fullbits)/256)):
        if not decrypt:
            bits = fullbits[(i*256):((i+1)*256)]
            bits = [x^y for (x,y) in zip(bits, last_bits)]
            res = pea.encrypt(bits, decrypt)
            last_bits = res
            bits_encrypt.extend(res)
        else:
            bits = fullbits[(i*256):((i+1)*256)]
            res = pea.encrypt(bits, decrypt)
            res = [x^y for (x,y) in zip(res, last_bits)]
            last_bits = bits
            bits_encrypt.extend(res)

    return bits_to_text(bits_encrypt)

def CFB(text, key, init_vector, nbits, decrypt=False):
    '''
        nbits: encryption length
    '''
    if 256 % nbits != 0:
            raise Exception('Length of nbits must be a factor of 256!')
    fullbits = text_to_bits(text)

    pea = PEA(key)
    qbits = init_vector
    bits_encrypt = []
    for i in range(int(len(fullbits)/nbits)):
        if not decrypt:
            bits = fullbits[(i*nbits):((i+1)*nbits)]
            enc_res = pea.encrypt(qbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res[:nbits])]
            bits_encrypt.extend(res)
            qbits = qbits[nbits:] + res
        else:
            bits = fullbits[(i*nbits):((i+1)*nbits)]
            enc_res = pea.encrypt(qbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res[:nbits])]
            bits_encrypt.extend(res)
            qbits = qbits[nbits:] + bits

    return bits_to_text(bits_encrypt)

def OFB(text, key, init_vector, nbits, decrypt=False):
    '''
        nbits: encryption length
    '''
    if 256%nbits != 0:
            raise Exception('Length of nbits must be a factor of 256!')
    fullbits = text_to_bits(text)

    pea = PEA(key)
    qbits = init_vector
    bits_encrypt = []
    for i in range(int(len(fullbits)/nbits)):
        if not decrypt:
            bits = fullbits[(i*nbits):((i+1)*nbits)]
            enc_res = pea.encrypt(qbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res[:nbits])]
            bits_encrypt.extend(res)
            qbits = qbits[nbits:] + enc_res[:nbits]
        else:
            bits = fullbits[(i*nbits):((i+1)*nbits)]
            enc_res = pea.encrypt(qbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res[:nbits])]
            bits_encrypt.extend(res)
            qbits = qbits[nbits:] + enc_res[:nbits]

    return bits_to_text(bits_encrypt)

def CTR(text, key, decrypt=False):
    fullbits = text_to_bits(text)

    pea = PEA(key)
    bits_encrypt = []
    count = create_ctr_start(key)
    for i in range(int(len(fullbits)/256)):
        if not decrypt:
            bits = fullbits[(i*256):((i+1)*256)]
            cbits = int_to_bits(count)
            enc_res = pea.encrypt(cbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res)]
            bits_encrypt.extend(res)
        else:
            bits = fullbits[(i*256):((i+1)*256)]
            cbits = int_to_bits(count)
            enc_res = pea.encrypt(cbits, False)
            res = [x^y for (x,y) in zip(bits, enc_res)]
            bits_encrypt.extend(res)
        count += 1

    return bits_to_text(bits_encrypt)

def create_ctr_start(key):
    bits = text_to_bits(key)
    sum = 0
    for bit in bits:
        sum += bit
    return sum

def int_to_bits(n):
    bits = [int(digit) for digit in bin(n)[2:]]
    if len(bits) < 256:
        return ([0] * (256-len(bits))) + bits
    return bits[256:]

def text_to_bits(text):
    bits_str = ''.join(['{:08b}'.format(ord(c)) for c in text])
    fullbits = [int(c) for c in bits_str]
    while (len(fullbits) % 256) != 0:
        fullbits.append(0)

    return fullbits

def bits_to_text(bits):
    text = ''
    for i in range(int(len(bits)/8)):
        byte = ''.join([str(x) for x in bits[(i*8):(i+1)*8]])
        text += chr(int(byte, 2))

    return text

def text_to_hex(text):
    hex_list = []
    for c in text:
        h = hex(ord(c))
        h = h[2:].upper()
        if len(h) == 1:
            h = '0' + h
        hex_list.append(h)

    return ' '.join(hex_list)

def freq_byte(bits):
    byte_set = Counter()
    for i in range(int(len(bits)/8)):
        byte = bits[(i*8):((i+1)*8)]
        bits_str = ''.join([str(x) for x in byte])
        decimal = int(bits_str, 2)
        byte_set.update([decimal])

    keys, vals = np.arange(0,256).tolist(), [0] * 256
    for key in list(byte_set.keys()):
        vals[key] = byte_set[key]
    return keys, vals

def plot_encryption(bits_plain, bits_cipher):
    keys1, vals1 = freq_byte(bits_plain)
    keys2, vals2 = freq_byte(bits_cipher)
    plt.plot(keys1, vals1, 'r-', keys2, vals2, 'b-')
    axes = plt.gca()
    axes.set_xlim([0,255])

    red_patch = mpatches.Patch(color='red', label='Plainteks')
    blue_patch = mpatches.Patch(color='blue', label='Cipherteks')
    plt.legend(handles=[red_patch, blue_patch])
    plt.show()

def write_to(file, text):
    with open(file, 'w') as f:
        f.write(text)

# if __name__=='__main__':
#     with open('mars.txt', 'r') as f:
#         text = f.read()
#     key = 'INFORMATIKA2018'
#     key_ = 'INFORMATIKA2017'
#     print(len(text))
#     bits = text_to_bits(text)
#     print(bits)
#     print(bits_to_text(bits))
#
#     # File names
#     in_name = 'lena.png'
#     out_name = 'lena_out.png'
#
#     # Read data and convert to a list of bits
#     in_bytes = np.fromfile(in_name, dtype = "uint8")
#     in_bits = np.unpackbits(in_bytes)
#     data = list(in_bits)
#     text = bits_to_text(data)
#
#     print('\nECB:')
#     enc = ECB(text, key)
#     hex_enc = text_to_hex(enc)
#     write_to('enc.txt', hex_enc)
#     start = time.time()
#     data = ECB(enc, key, True)
#     end = time.time()
#     # plot_encryption(text_to_bits(text), text_to_bits(enc))
#     print(end - start)
#
#     # Convert the list of bits back to bytes and save
#     out_bits = np.array(data)
#     out_bytes = np.packbits(out_bits)
#     out_bytes.tofile(out_name)
#
#     """
#     print('\nCBC:')
#     iv = [1] * 256
#     enc = CBC(text, key, iv)
#     print(text_to_hex(enc))
#     start = time.time()
#     print(CBC(enc, key, iv, True))
#     end = time.time()
#     # plot_encryption(text_to_bits(text), text_to_bits(enc))
#     print(end - start)
#
#     print('\nCFB:')
#     iv = [1] * 256
#     enc = CFB(text, key, iv, 256)
#     print(text_to_hex(enc))
#     start = time.time()
#     print(CFB(enc, key, iv, 256, True))
#     end = time.time()
#     # plot_encryption(text_to_bits(text), text_to_bits(enc))
#     print(end - start)
#
#     print('\nOFB:')
#     iv = [1] * 256
#     enc = OFB(text, key, iv, 256)
#     print(text_to_hex(enc))
#     start = time.time()
#     print(OFB(enc, key, iv, 256, True))
#     end = time.time()
#     # plot_encryption(text_to_bits(text), text_to_bits(enc))
#     print(end - start)
#
#     print('\nCTR:')
#     enc = CTR(text, key)
#     print(text_to_hex(enc))
#     start = time.time()
#     print(CTR(enc, key, True))
#     end = time.time()
#     # plot_encryption(text_to_bits(text), text_to_bits(enc))
#     print(end - start)
#     """
