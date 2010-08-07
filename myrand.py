"""A collection of implementations."""

class Random(object):
    """A base class for random number generators.

    Children should override `randint()`.
    """

    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000000)
        self.seed = seed

    def __iter__(self):
        while True:
            yield self.randint()

    def randint(self):
        """Generate another 32-bit random number."""
        raise NotImplementedError("override this")

    def randfloat(self):
        return self.randint() / float(2**32)

    def randbitstream(self):
        while True:
            x = self.randint()
            for i in range(32):
                yield x % 2
                x = x >> 1


class NewRandom(Random):
    """A custom random number generator."""

    # 10 random large primes
    K = [3939623148640414471,
         2720930543666750453,
         2007477920046856561,
         1823091508454384321,
         4151478475954908493,
         3180680310717437219,
         2553681038050673093,
         3860821396807810507,
         1464252920780449187,
         3143737298900961481]

    def __init__(self, seed=None):
        super(NewRandom, self).__init__(seed=seed)
        self.prev = self.seed
        #self.c = 13478653040317
        self.ki = self.seed % 10

    def randint(self):
        prev = self.prev
        ##s = ''.join(str(self.c * self.prev))
        s = ''.join(reversed(str(self.K[self.ki] * self.prev)))
        self.ki = (self.ki + int(s[len(s) // 2])) % 10
        self.prev = int(s[::2]) % (2 ** 64)
        return self.prev % (2 ** 32)


class LCG(Random):
    """A bad RNG reference implementation."""
    # Used for testing the test suite.
    # If you examine the test plot, you will clearly see artifacts.

    a = 22695477
    c = 1

    def __init__(self, seed=None):
        super(LCG, self).__init__(seed=seed)
        self.prev = self.seed

    def randint(self):
        x = (self.a * self.prev + self.c) % (2**32)
        self.prev = x
        return x


class BBS(Random):
    """A good RNG reference implementation.

    This is the B.B.S. RNG; for more information see
    http://en.wikipedia.org/wiki/Blum_Blum_Shub
    """
    # Used for testing the test suite.

    M = 100385543 * 100385123

    def __init__(self, seed=None):
        super(BBS, self).__init__(seed=seed)
        self.prev = self.seed

    def randint(self):
        x = (self.prev * self.prev) % self.M
        self.prev = x
        return x
