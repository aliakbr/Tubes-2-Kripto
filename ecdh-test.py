from ECDH import ECDH

ecdh = ECDH()

alice_private_key, alice_public_key = ecdh.make_pair()
print("Alice's private key:", hex(alice_private_key))
print("Alice's public key: (0x{:x}, 0x{:x})".format(*alice_public_key))

bob_private_key, bob_public_key = ecdh.make_pair()
print("Bob's private key:", hex(bob_private_key))
print("Bob's public key: (0x{:x}, 0x{:x})".format(*bob_public_key))

s1 = ecdh.scalar_multiplication(alice_private_key, bob_public_key)
s2 = ecdh.scalar_multiplication(bob_private_key, alice_public_key)
assert s1 == s2

print('Shared secret: (0x{:x}, 0x{:x})'.format(*s1))
