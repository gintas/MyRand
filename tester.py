#!/usr/bin/python
"""An RNG testing suite."""

import zlib
from math import sqrt, factorial

# Constants.
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768

PERMUTATION_SIZE = 5


def main():
    """Main suite."""
    import myrand
    test(myrand.NewRandom)
    #test(myrand.LCG)
    #test(myrand.BBS)


def test(cls, seed=123123123, iterations=200000):
    """Run a suite of tests on the given random number generator class.

    `iterations` indicates how many random numbers to generate.

    Prints results to standard output. Creates a PNG image file named after the
    class.
    """
    test_name = cls.__name__
    print 'TEST: %s (%d iterations)' % (test_name, iterations)
    print cls.__doc__
    print '---'

    rng = cls(seed=seed)
    s = ''

    # Generate numbers, collect bucket information.
    # Two bucket bins are created, one for the most significant byte of the
    # int and one for the least significant byte. Later we check that the
    # buckets are evenly distributed.
    lsb_bins = {}
    msb_bins = {}
    for i in range(256):
        lsb_bins[i] = msb_bins[i] = 0
    for i in xrange(iterations):
        x = rng.randint()
        lsb_bins[x % 256] += 1
        msb_bins[(x >> 24) % 256] += 1

        for j in range(4):
            s += chr(x % 256)
            x = x >> 8

    print '== Least-significant-byte buckets =='
    examine_buckets(lsb_bins, iterations)
    print '== Most-significant-byte buckets =='
    examine_buckets(msb_bins, iterations)
    print '== Permutations =='
    check_permutation_distribution(s)
    print '==='

    print 'Period length:', find_period(s)

    print 'Gzip factor:', gzip_factor(s)

    plot_filename = test_name.lower() + '.png'
    print 'Drawing plot (%s)...' % plot_filename
    draw_plot(s, filename=plot_filename)

    print '--------------------------------------------------'


def examine_buckets(bins, iterations):
    if (min(bins.keys()), max(bins.keys())) != (0, 256):
        print 'WARNING: bucket range:', len(bins.keys())
    if len(bins.keys()) != 256:
        print 'WARNING: bucket count:', len(bins.keys())
    print 'bucket spread:', min(bins.values()), max(bins.values()), '(should be around %d)' % (iterations / 256)
    print 'bucket stdev:', stdev(bins.values())
    x = [p[0] for p in bins.items()]
    y = [p[1] for p in bins.items()]
    a, b = linreg(x, y)
    print 'linear regression: a=%.03f, b=%.03f' % (a, b)


def linreg(X, Y):
    """Calculate linear regression between X and Y."""
    # Borrowed from http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
    if len(X) != len(Y):
        raise ValueError, 'unequal length'
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in map(None, X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

    meanerror = residual = 0.0
    for x, y in map(None, X, Y):
        meanerror = meanerror + (y - Sy/N)**2
        residual = residual + (y - a * x - b)**2
    RR = 1 - residual/meanerror
    ss = residual / (N-2)
    Var_a, Var_b = ss * N / det, ss * Sxx / det

    return a, b


def stdev(v):
    """Return standard deviation of a list."""
    mean = sum(v) / float(len(v))
    std = 0
    for a in v:
        std = std + (a - mean)**2
    std = sqrt(std / float(len(v)-1))
    return std


def find_period(s, block=1024):
    """Try to find a period in the given string.

    Returns a position or n/a.
    """
    # Skip the initial `block` bytes.
    part = s[block:block*2]
    pos = s[block*2:].find(part)
    if pos != -1:
        return pos + block
    else:
        return 'n/a'


def gzip_factor(s):
    """Check how well a string compresses.

    Returns a float. If the factor is significantly below 1, the string
    probably has significant patterns.
    """
    return float(len(zlib.compress(s))) / len(s)


def to_bits(s):
    """Convert an 8-bit string to a list of bits."""
    bits = []
    for c in s:
        x = ord(c)
        for i in range(8):
            bits.append(x % 2)
            x = x >> 1
    return bits


def draw_plot(s, filename='result.png'):
    """Draw a B&W plot of the bits from a given 8-bit string."""
    n_pixels = IMAGE_HEIGHT * IMAGE_WIDTH
    plottable = s[:n_pixels // 8]

    try:
        import Image
    except ImportError:
        print 'PIL not available! Unable to draw plot.'
        return
    img = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT))
    img.putdata(to_bits(plottable))
    img.save(filename)


def order(seq):
    """Return order of numbers in a sequence.

        >>> order([1, 3, 5, 7])
        '1234'
        >>> order([1, 5, 5, 7])
        '1234'
        >>> order([7, 5, 3, 1])
        '4321'
        >>> order([9, 3, 5, 2])
        '4231'

    """
    result = [''] * len(seq)
    for i in range(len(seq)):
        for j in range(len(seq)):
            if seq[j] == min(seq):
                result[j] = str(i+1)
                seq[j] = 2 ** 40 # infinity
                break
    return ''.join(result)


def check_permutation_distribution(s, block=2**15):
    """Check the distribution of permutations of consecutive numbers.

    `block` is the size of the subset of the character string to run the
    check on.
    """
    s = s[:block]
    bins = {}
    for i in range(len(s)-PERMUTATION_SIZE):
        seq = [ord(c) for c in s[i:i+PERMUTATION_SIZE]]
        key = order(seq)
        bins.setdefault(key, 0)
        bins[key] += 1
    if len(bins.keys()) != factorial(PERMUTATION_SIZE):
        print 'WARNING: permutation bucket count: %s (should be %s)' % (
                len(bins.keys()), factorial(PERMUTATION_SIZE))
    print 'permutation bucket spread:', min(bins.values()), max(bins.values())
    print 'permutation bucket stdev:', stdev(bins.values())



if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
