
#!/usr/bin/env python3

import random

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b%a,a)
    return (g, x - (b//a) * y, y)

def inverse_mod(a, m):
    if a < 0:
        # k ** -1 = p - (-k) ** -1  (mod p)
        return m - inverse_mod(-a, m)

    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('No modular inverse')
    return x%m

class ECDH:
    def __init__(self,
                 p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
                 a = 0,
                 b = 7,
                 g = (0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
                      0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8),
                 n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141):
        """
            Create curve with
            p : prime
            a : a coefficient of EC
            b : b coefficient of EC
            g : basepoint
            n : order for random and generating private key
        """
        self.p = p
        self.a = a
        self.b = b
        self.g = g
        self.n = n

    def is_on_curve(self, point):
        """
            return True if the point is on curve
        """
        if point is None:
            # Point is None mean point at the infinity
            return True

        x, y = point

        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def point_neg(self, point):
        """
            Returns -point.
        """
        assert self.is_on_curve(point)
        if point is None:
            return None
        x, y = point
        result = (x, -y % self.p)
        assert self.is_on_curve(result)
        return result

    def add_point(self, point1, point2):
        """
            Point addition according to EC Group Law
        """
        assert self.is_on_curve(point1)
        assert self.is_on_curve(point2)

        if point1 is None:
            return point2
        if point2 is None:
            return point1

        x1, y1 = point1
        x2, y2 = point2

        if x1 == x2 and y1 != y2:
            # point1 + (-point1) = O
            return None

        if x1 == x2:
            # (2P)
            m = (3 * x1 * x1 + self.a) * inverse_mod(2 * y1, self.p)
        else:
            # P+Q
            m = (y1 - y2) * inverse_mod(x1 - x2, self.p)

        x3 = m * m - x1 - x2
        y3 = y1 + m * (x3 - x1)
        result = (x3 % self.p, -y3 % self.p)
        assert self.is_on_curve(result)
        return result

    def scalar_multiplication(self, k, point):
        """
            return kP from EC group law
        """
        assert self.is_on_curve(point)
        if (k % self.n == 0) or (point is None):
            return None

        if k < 0:
            return scalar_multiplication(-k, self.point_neg(point))

        result = None
        addend = point

        while k:
            if k & 1:
                # Add.
                result = self.add_point(result, addend)
            # Double.
            addend = self.add_point(addend, addend)
            k >>= 1

        assert self.is_on_curve(result)

        return result

    def make_pair(self):
        """
            Generate public and private key
        """
        private_key = random.randrange(1, self.n)
        public_key = self.scalar_multiplication(private_key, self.g)
        return private_key, public_key
